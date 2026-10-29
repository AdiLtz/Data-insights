"""Local InsightSQL HTTP application."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import SplitResult, urlparse

from .database import QueryExecutionError, ReadOnlyDatabase
from .generator import GenerationError, SQLGenerator
from .history import QueryHistory
from .sql_guard import SQLValidationError


MAX_REQUEST_BYTES = 16_384
STATIC_DIRECTORY = Path(__file__).resolve().parent.parent / "static"
LOGGER = logging.getLogger("insightsql")


def create_handler(
    database: ReadOnlyDatabase,
    generator: SQLGenerator,
    history: QueryHistory,
) -> type[BaseHTTPRequestHandler]:
    class InsightSQLHandler(BaseHTTPRequestHandler):
        server_version = "InsightSQL/1.0"

        def log_message(self, format_string: str, *args: Any) -> None:
            LOGGER.info(
                "http_request",
                extra={
                    "client_ip": self.client_address[0],
                    "request_line": format_string % args,
                },
            )

        def _send_json(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, object]:
            content_length = self.headers.get("Content-Length", "")
            if not content_length.isdigit():
                raise ValueError("A valid Content-Length header is required.")
            size = int(content_length)
            if size > MAX_REQUEST_BYTES:
                raise ValueError("Request body is too large.")
            try:
                value = json.loads(self.rfile.read(size))
            except json.JSONDecodeError as error:
                raise ValueError("Request body must be valid JSON.") from error
            if not isinstance(value, dict):
                raise ValueError("Request body must be a JSON object.")
            return value

        def _local_request_origin(self) -> SplitResult | None:
            try:
                request_origin = urlparse("//" + self.headers.get("Host", ""))
                if request_origin.hostname in {"localhost", "127.0.0.1", "::1"}:
                    return request_origin
            except ValueError:
                pass
            return None

        def _same_origin(self) -> bool:
            request_origin = self._local_request_origin()
            if request_origin is None:
                return False
            origin = self.headers.get("Origin")
            if not origin:
                return True
            try:
                parsed = urlparse(origin)
                return (
                    parsed.scheme == "http"
                    and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
                    and parsed.hostname == request_origin.hostname
                    and parsed.port == request_origin.port
                )
            except ValueError:
                return False

        def do_GET(self) -> None:
            if self._local_request_origin() is None:
                self._send_json(403, {"error": "Requests must use a local host name."})
                return
            try:
                self._handle_get(urlparse(self.path).path)
            except Exception:
                LOGGER.exception("Unhandled GET request error")
                self._send_json(
                    500,
                    {"error": "Something went wrong. Check the server log for details."},
                )

        def _handle_get(self, path: str) -> None:
            if path == "/":
                self._send_static("index.html", "text/html; charset=utf-8")
            elif path == "/app.css":
                self._send_static("app.css", "text/css; charset=utf-8")
            elif path == "/app.js":
                self._send_static("app.js", "text/javascript; charset=utf-8")
            elif path == "/api/history":
                self._send_json(200, {"history": history.recent()})
            elif path == "/api/schema":
                self._send_json(200, {"tables": database.schema_context()})
            elif path == "/api/health":
                self._send_json(200, {"status": "ok", "database": "read-only"})
            else:
                self._send_json(404, {"error": "Not found."})

        def _send_static(self, filename: str, content_type: str) -> None:
            path = STATIC_DIRECTORY / filename
            try:
                body = path.read_bytes()
            except OSError:
                self._send_json(500, {"error": "The application UI could not be loaded."})
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; script-src 'self'; "
                "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
                "frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if not self._same_origin():
                self._send_json(403, {"error": "Cross-origin requests are not allowed."})
                return

            path = urlparse(self.path).path
            try:
                payload = self._read_json()
                if path == "/api/generate":
                    self._generate(payload)
                elif path == "/api/execute":
                    self._execute(payload)
                else:
                    self._send_json(404, {"error": "Not found."})
            except ValueError as error:
                self._send_json(400, {"error": str(error)})
            except Exception:
                LOGGER.exception("Unhandled API error")
                self._send_json(
                    500,
                    {"error": "Something went wrong. Check the server log for details."},
                )

        def _generate(self, payload: dict[str, object]) -> None:
            question = payload.get("question")
            if not isinstance(question, str):
                raise ValueError("Question must be text.")
            try:
                sql = generator.generate(question)
                self._send_json(200, {"sql": sql})
            except GenerationError as error:
                self._send_json(422, {"error": str(error)})

        def _execute(self, payload: dict[str, object]) -> None:
            question = payload.get("question", "")
            sql = payload.get("sql")
            if not isinstance(question, str) or not isinstance(sql, str):
                raise ValueError("Question and SQL must be text.")

            try:
                result = database.execute(sql)
                history.add(
                    question, sql, "success", int(result["row_count"]), None
                )
                self._send_json(200, {"result": result})
            except (SQLValidationError, QueryExecutionError) as error:
                history.add(question, sql, "error", None, str(error))
                self._send_json(422, {"error": str(error)})

    return InsightSQLHandler


def serve(
    database_path: Path,
    history_path: Path,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("For safety, InsightSQL only binds to the local machine.")
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    database = ReadOnlyDatabase(database_path)
    generator = SQLGenerator(database.path)
    history = QueryHistory(history_path)
    server = ThreadingHTTPServer(
        (host, port),
        create_handler(database, generator, history),
    )
    server.daemon_threads = True
    LOGGER.info("InsightSQL listening at http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("InsightSQL shutting down")
    finally:
        server.server_close()
