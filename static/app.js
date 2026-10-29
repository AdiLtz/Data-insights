const questionInput = document.querySelector("#question");
const sqlInput = document.querySelector("#sql");
const sqlPanel = document.querySelector("#sql-panel");
const resultPanel = document.querySelector("#result-panel");
const generateButton = document.querySelector("#generate-button");
const runButton = document.querySelector("#run-button");
const toast = document.querySelector("#toast");
let toastTimer;

async function requestJson(path, payload) {
  const options = payload
    ? {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    : { headers: { Accept: "application/json" } };
  const response = await fetch(path, options);
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an unreadable response.");
  }
  if (!response.ok) throw new Error(data.error || "The request could not be completed.");
  return data;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3500);
}

function setBusy(button, busy, label) {
  button.disabled = busy;
  button.dataset.originalText ??= button.textContent;
  button.textContent = busy ? label : button.dataset.originalText;
}

async function generateSQL() {
  const question = questionInput.value.trim();
  if (!question) {
    showToast("Enter a question to get started.");
    questionInput.focus();
    return;
  }

  setBusy(generateButton, true, "Generating…");
  try {
    const data = await requestJson("/api/generate", { question });
    sqlInput.value = data.sql;
    sqlPanel.hidden = false;
    resultPanel.hidden = true;
    sqlPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    sqlInput.focus();
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(generateButton, false, "Generate SQL");
  }
}

async function runSQL() {
  const sql = sqlInput.value.trim();
  if (!sql) {
    showToast("Generate or enter a SELECT query first.");
    sqlInput.focus();
    return;
  }

  setBusy(runButton, true, "Running…");
  resultPanel.hidden = false;
  document.querySelector("#result-message").hidden = true;
  document.querySelector("#table-wrap").replaceChildren();
  document.querySelector("#result-count").textContent = "";

  try {
    const data = await requestJson("/api/execute", {
      question: questionInput.value.trim(),
      sql,
    });
    renderResults(data.result);
    refreshHistory();
  } catch (error) {
    showResultError(error.message);
    refreshHistory();
  } finally {
    setBusy(runButton, false, "▶ Run query");
  }
}

function renderResults(result) {
  const count = result.row_count;
  document.querySelector("#result-count").textContent =
    `${count} row${count === 1 ? "" : "s"}${result.truncated ? " · output capped" : ""}`;
  const wrapper = document.querySelector("#table-wrap");
  if (!result.columns.length) {
    showResultError("The query did not return any columns.");
    return;
  }
  if (!result.rows.length) {
    wrapper.innerHTML = '<div class="empty-results">No matching records found.</div>';
    return;
  }

  const table = document.createElement("table");
  const head = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const column of result.columns) {
    const th = document.createElement("th");
    th.textContent = column;
    headerRow.append(th);
  }
  head.append(headerRow);
  const body = document.createElement("tbody");
  for (const row of result.rows) {
    const tr = document.createElement("tr");
    for (const column of result.columns) {
      const td = document.createElement("td");
      const value = row[column];
      td.textContent = value === null ? "—" : String(value);
      tr.append(td);
    }
    body.append(tr);
  }
  table.append(head, body);
  wrapper.append(table);
}

function showResultError(message) {
  const box = document.querySelector("#result-message");
  box.textContent = message;
  box.hidden = false;
  document.querySelector("#result-count").textContent = "Query not run";
}

async function refreshSchema() {
  const list = document.querySelector("#schema-list");
  try {
    const { tables } = await requestJson("/api/schema");
    list.replaceChildren();
    for (const table of tables) {
      const item = document.createElement("div");
      item.className = "schema-item";
      const name = document.createElement("strong");
      name.textContent = table.name;
      const columns = document.createElement("span");
      columns.textContent = table.columns.join(" · ");
      item.append(name, columns);
      list.append(item);
    }
  } catch (error) {
    list.textContent = error.message;
  }
}

async function refreshHistory() {
  const list = document.querySelector("#history-list");
  try {
    const { history } = await requestJson("/api/history");
    list.replaceChildren();
    if (!history.length) {
      const empty = document.createElement("p");
      empty.className = "history-empty";
      empty.textContent = "Your executed queries will appear here. History is stored only on this device.";
      list.append(empty);
      return;
    }
    for (const entry of history) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "history-entry";
      item.title = "Load this query";
      const top = document.createElement("span");
      top.className = "history-entry-top";
      const question = document.createElement("span");
      question.className = "history-question";
      question.textContent = entry.question || entry.sql_text;
      const status = document.createElement("span");
      status.className = `history-status${entry.status === "success" ? "" : " error"}`;
      status.setAttribute("aria-label", entry.status);
      const meta = document.createElement("span");
      meta.className = "history-meta";
      const date = new Date(entry.created_at);
      meta.textContent = `${Number.isNaN(date.valueOf()) ? entry.created_at : date.toLocaleString()} · ${
        entry.status === "success" ? `${entry.row_count} rows` : "not run"
      }`;
      top.append(question, status);
      item.append(top, meta);
      item.addEventListener("click", () => {
        questionInput.value = entry.question || "";
        sqlInput.value = entry.sql_text;
        sqlPanel.hidden = false;
        resultPanel.hidden = true;
        sqlPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      });
      list.append(item);
    }
  } catch (error) {
    list.textContent = error.message;
  }
}

generateButton.addEventListener("click", generateSQL);
runButton.addEventListener("click", runSQL);
document.querySelector("#refresh-history").addEventListener("click", refreshHistory);
document.querySelectorAll(".example-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    questionInput.value = chip.textContent;
    questionInput.focus();
  });
});
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) generateSQL();
});
sqlInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) runSQL();
});

refreshSchema();
refreshHistory();
