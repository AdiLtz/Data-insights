"""Start the local InsightSQL application."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from insightsql.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local InsightSQL app.")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parent / "employee_management.db",
        help="Path to the existing SQLite database (default: employee_management.db).",
    )
    parser.add_argument(
        "--history",
        type=Path,
        default=Path(__file__).resolve().parent / ".insightsql_history.db",
        help="Path for local query history.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        serve(args.db, args.history, args.host, args.port)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
