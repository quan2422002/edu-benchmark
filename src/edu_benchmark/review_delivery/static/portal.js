"use strict";

const state = {
  catalog: null,
  fragments: [],
  filtered: [],
  page: 1,
  pageSize: 20,
  selectedPdf: null,
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function inlineMarkdown(value) {
  let text = escapeHtml(value);
  text = text.replace(/!\[([^\]]*)\]\((\/media\/image\/[a-f0-9]+)\)/g,
    (_, alt, src) => `<figure><img loading="lazy" src="${src}" alt="${alt || "Ảnh học liệu"}"><figcaption>${alt}</figcaption></figure>`);
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
  return text;
}

function renderMarkdown(markdown) {
  const lines = String(markdown ?? "").replaceAll("\r\n", "\n").split("\n");
  const html = [];
  let index = 0;
  let inCode = false;
  let codeLines = [];
  while (index < lines.length) {
    const line = lines[index];
    if (line.trim().startsWith("```")) {
      if (inCode) {
        html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
        codeLines = [];
        inCode = false;
      } else {
        inCode = true;
      }
      index += 1;
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      index += 1;
      continue;
    }
    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) {
      const level = Math.min(6, heading[1].length + 1);
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      index += 1;
      continue;
    }
    if (line.includes("|") && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1])) {
      const tableLines = [line];
      index += 2;
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        tableLines.push(lines[index]);
        index += 1;
      }
      const splitRow = (row) => row.trim().replace(/^\|/, "").replace(/\|$/, "").split("|");
      const header = splitRow(tableLines[0]);
      const body = tableLines.slice(1).map(splitRow);
      html.push("<table><thead><tr>" + header.map((cell) => `<th>${inlineMarkdown(cell.trim())}</th>`).join("") + "</tr></thead><tbody>");
      for (const row of body) {
        html.push("<tr>" + row.map((cell) => `<td>${inlineMarkdown(cell.trim())}</td>`).join("") + "</tr>");
      }
      html.push("</tbody></table>");
      continue;
    }
    if (/^\s*[-*+]\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^\s*[-*+]\s+/.test(lines[index])) {
        items.push(lines[index].replace(/^\s*[-*+]\s+/, ""));
        index += 1;
      }
      html.push("<ul>" + items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("") + "</ul>");
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^\s*\d+[.)]\s+/.test(lines[index])) {
        items.push(lines[index].replace(/^\s*\d+[.)]\s+/, ""));
        index += 1;
      }
      html.push("<ol>" + items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("") + "</ol>");
      continue;
    }
    if (/^\s*>\s?/.test(line)) {
      html.push(`<blockquote>${inlineMarkdown(line.replace(/^\s*>\s?/, ""))}</blockquote>`);
      index += 1;
      continue;
    }
    if (!line.trim()) {
      index += 1;
      continue;
    }
    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && lines[index].trim() && !/^(#{1,6})\s+/.test(lines[index])) {
      if (/^\s*[-*+]\s+/.test(lines[index]) || /^\s*\d+[.)]\s+/.test(lines[index])) break;
      paragraph.push(lines[index].trim());
      index += 1;
    }
    html.push(`<p>${inlineMarkdown(paragraph.join(" "))}</p>`);
  }
  if (inCode) html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
  return html.join("");
}

function fillSelect(id, values, labeler = (value) => value) {
  const select = $(id);
  for (const value of values) {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = labeler(value);
    select.append(option);
  }
}

function replaceSelectOptions(id, values, defaultLabel) {
  const select = $(id);
  const previousValue = select.value;
  select.replaceChildren();
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = defaultLabel;
  select.append(defaultOption);
  for (const value of values) {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = String(value);
    select.append(option);
  }
  select.value = values.includes(previousValue) ? previousValue : "";
}

function updateLessonOptions() {
  const selectedBook = $("book-filter").value;
  const lessons = [...new Set(
    state.fragments
      .filter((fragment) => !selectedBook || fragment.book_title === selectedBook)
      .map((fragment) => fragment.lesson_title)
      .filter(Boolean)
  )].sort((left, right) => left.localeCompare(right, "vi"));
  replaceSelectOptions("lesson-filter", lessons, "Tất cả bài học");
}

function setupFilters() {
  const options = state.catalog.options;
  fillSelect("book-filter", options.books);
  updateLessonOptions();
  fillSelect("book-grade-filter", options.grades, (value) => `Lớp ${value}`);
  fillSelect("book-material-filter", ["SGK", "SGV", "SBT"]);
}

function queryMatcher() {
  const query = $("search-query").value.trim();
  const regexMode = $("regex-mode").checked;
  $("search-error").textContent = "";
  if (!query) return () => true;
  if (!regexMode) {
    const needle = query.toLocaleLowerCase("vi");
    return (fragment) => fragment.search_text.includes(needle);
  }
  if (query.length > state.catalog.max_regex_length) {
    $("search-error").textContent = `Biểu thức tối đa ${state.catalog.max_regex_length} ký tự.`;
    return null;
  }
  try {
    const expression = new RegExp(query, "iu");
    return (fragment) => expression.test(fragment.search_text_raw);
  } catch (error) {
    $("search-error").textContent = `Biểu thức chưa hợp lệ: ${error.message}`;
    return null;
  }
}

function applyFilters() {
  const matcher = queryMatcher();
  if (!matcher) return;
  const book = $("book-filter").value;
  const lesson = $("lesson-filter").value;
  state.filtered = state.fragments.filter((fragment) =>
    (!book || fragment.book_title === book) &&
    (!lesson || fragment.lesson_title === lesson) &&
    matcher(fragment)
  );
  state.page = 1;
  renderResults();
}

function fragmentCard(fragment) {
  const article = document.createElement("article");
  article.className = "fragment-card";
  const header = document.createElement("div");
  header.className = "fragment-card-header";
  header.innerHTML = `
    <strong class="fragment-id">${escapeHtml(fragment.fragment_id)}</strong>
    <div class="chips">
      <span class="chip">Lớp ${fragment.grade}</span>
      <span class="chip">${escapeHtml(fragment.material_type)}</span>
      <span class="chip">${escapeHtml(fragment.fragment_type === "table" ? "Bảng" : "Văn bản")}</span>
      <span class="chip ${fragment.searchable ? "searchable" : "storage"}">${fragment.searchable ? "Được dùng để truy xuất" : "Chỉ lưu để bảo toàn nguồn"}</span>
      ${fragment.image_count ? `<span class="chip">${fragment.image_count} ảnh</span>` : ""}
    </div>
    <p class="section-path"><strong>${escapeHtml(fragment.book_title)}</strong> · ${escapeHtml(fragment.section_path || fragment.lesson_title)}</p>`;
  const body = document.createElement("div");
  body.className = "markdown-body";
  body.innerHTML = renderMarkdown(fragment.markdown_text);
  article.append(header, body);
  return article;
}

function renderPagination(totalPages) {
  const navigation = $("pagination");
  navigation.replaceChildren();
  if (totalPages <= 1) return;
  const addButton = (label, page, disabled = false, active = false) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.disabled = disabled;
    if (active) button.classList.add("active");
    button.addEventListener("click", () => { state.page = page; renderResults(); window.scrollTo({top: 150, behavior: "smooth"}); });
    navigation.append(button);
  };
  addButton("‹", Math.max(1, state.page - 1), state.page === 1);
  const pages = new Set([1, totalPages, state.page - 1, state.page, state.page + 1]);
  let previous = 0;
  for (const page of [...pages].filter((value) => value >= 1 && value <= totalPages).sort((a, b) => a - b)) {
    if (previous && page - previous > 1) {
      const span = document.createElement("span"); span.textContent = "…"; navigation.append(span);
    }
    addButton(String(page), page, false, page === state.page);
    previous = page;
  }
  addButton("›", Math.min(totalPages, state.page + 1), state.page === totalPages);
}

function renderResults() {
  const total = state.filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
  state.page = Math.min(state.page, totalPages);
  $("result-count").textContent = `${total.toLocaleString("vi-VN")} kết quả phù hợp`;
  const container = $("fragment-results");
  container.replaceChildren();
  $("empty-state").classList.toggle("hidden", total !== 0);
  const start = (state.page - 1) * state.pageSize;
  for (const fragment of state.filtered.slice(start, start + state.pageSize)) {
    container.append(fragmentCard(fragment));
  }
  renderPagination(totalPages);
}

function resetFilters() {
  for (const id of ["search-query", "book-filter", "lesson-filter"]) {
    $(id).value = "";
  }
  $("regex-mode").checked = false;
  updateLessonOptions();
  applyFilters();
}

function renderBooks() {
  const grade = $("book-grade-filter").value;
  const material = $("book-material-filter").value;
  const books = state.catalog.pdfs.filter((book) =>
    (!grade || String(book.grade) === grade) && (!material || book.material_type === material)
  );
  const list = $("book-list");
  list.replaceChildren();
  for (const book of books) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "book-card" + (state.selectedPdf === book.filename ? " active" : "");
    button.innerHTML = `<strong>${escapeHtml(book.title)}</strong><span>${escapeHtml(book.source_label)} · ${(book.size_bytes / 1024 / 1024).toFixed(1)} MB</span>`;
    button.addEventListener("click", () => {
      state.selectedPdf = book.filename;
      $("pdf-placeholder").classList.add("hidden");
      const viewer = $("pdf-viewer");
      viewer.src = book.url;
      viewer.classList.remove("hidden");
      renderBooks();
    });
    list.append(button);
  }
}

function bindEvents() {
  document.querySelectorAll(".tab-button").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".tab-button").forEach((item) => item.classList.toggle("active", item === button));
    document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
    $(`tab-${button.dataset.tab}`).classList.add("active");
  }));
  let timer = null;
  $("search-query").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(applyFilters, 180); });
  for (const id of ["regex-mode", "lesson-filter"]) {
    $(id).addEventListener("change", applyFilters);
  }
  $("book-filter").addEventListener("change", () => {
    updateLessonOptions();
    applyFilters();
  });
  $("page-size").addEventListener("change", () => { state.pageSize = Number($("page-size").value); state.page = 1; renderResults(); });
  $("reset-filters").addEventListener("click", resetFilters);
  $("book-grade-filter").addEventListener("change", renderBooks);
  $("book-material-filter").addEventListener("change", renderBooks);
}

async function initialize() {
  try {
    const [catalogResponse, fragmentResponse] = await Promise.all([fetch("/api/catalog"), fetch("/api/fragments")]);
    if (!catalogResponse.ok || !fragmentResponse.ok) throw new Error("Không tải được dữ liệu học liệu.");
    state.catalog = await catalogResponse.json();
    const payload = await fragmentResponse.json();
    state.fragments = payload.fragments.map((fragment) => {
      const searchTextRaw = [fragment.fragment_id, fragment.section_path, fragment.lesson_title, fragment.book_title, fragment.markdown_text].join("\n");
      return {...fragment, search_text_raw: searchTextRaw, search_text: searchTextRaw.toLocaleLowerCase("vi")};
    });
    state.filtered = state.fragments;
    $("header-fragment-count").textContent = state.fragments.length.toLocaleString("vi-VN");
    $("loading-state").classList.add("hidden");
    setupFilters();
    bindEvents();
    renderResults();
    renderBooks();
  } catch (error) {
    $("loading-state").textContent = `Không thể mở cổng học liệu: ${error.message}`;
  }
}

initialize();
