const COMPLEXES = [
  { id: "sample-apt", name: "Sample Apartment", area: "84.9 m2" },
];

const currency = new Intl.NumberFormat("ko-KR");

document.addEventListener("DOMContentLoaded", () => {
  initComplexSelect();
  renderHealth();
  renderSelectedComplex();
  document.getElementById("complexSelect").addEventListener("change", renderSelectedComplex);
});

function initComplexSelect() {
  const select = document.getElementById("complexSelect");
  select.replaceChildren(
    ...COMPLEXES.map((complex) => {
      const option = document.createElement("option");
      option.value = complex.id;
      option.textContent = `${complex.name} (${complex.area})`;
      return option;
    }),
  );
}

async function renderHealth() {
  try {
    const health = await fetchJson("data/state/health.json");
    const latest = health.latest || health.runs?.at?.(-1);
    if (!latest) {
      setStatus("unknown", "상태 미확인", "실행 기록이 아직 없습니다.", "-");
      setMetrics({});
      return;
    }

    setStatus(latest.status, statusLabel(latest.status), latest.reason || "completed", latest.finished_at || "-");
    setMetrics(latest.counts || {});
  } catch (error) {
    setStatus("failed", "상태 오류", "상태 파일을 불러오지 못했습니다.", "-");
    setMetrics({});
  }
}

function setStatus(status, label, reason, finishedAt) {
  const badge = document.getElementById("statusBadge");
  badge.className = `status-badge status-${status || "unknown"}`;
  badge.textContent = label;
  document.getElementById("statusReason").textContent = reason;
  document.getElementById("lastRunTime").textContent = formatTime(finishedAt);
}

function setMetrics(counts) {
  document.getElementById("watchedComplexes").textContent = numberOrDash(counts.watched_complexes);
  document.getElementById("validListings").textContent = numberOrDash(counts.valid_listings);
  document.getElementById("approvedCandidates").textContent = numberOrDash(counts.approved_candidates);
  document.getElementById("notificationsSent").textContent = numberOrDash(counts.notifications_sent);
}

async function renderSelectedComplex() {
  const complexId = document.getElementById("complexSelect").value || COMPLEXES[0].id;
  await Promise.all([renderHistory(complexId), renderFeed(complexId)]);
}

async function renderHistory(complexId) {
  const canvas = document.getElementById("historyChart");
  const empty = document.getElementById("chartEmpty");

  try {
    const payload = await fetchJson(`data/history/${complexId}.json`);
    const history = Array.isArray(payload.history) ? payload.history : [];
    if (history.length === 0 || !hasPriceData(history)) {
      canvas.hidden = true;
      empty.hidden = false;
      empty.textContent = "히스토리 데이터가 아직 없습니다.";
      return;
    }
    empty.hidden = true;
    canvas.hidden = false;
    drawHistoryChart(canvas, history);
  } catch (error) {
    canvas.hidden = true;
    empty.hidden = false;
    empty.textContent = "히스토리 데이터를 불러오지 못했습니다.";
  }
}

async function renderFeed(complexId) {
  const list = document.getElementById("feedList");
  const count = document.getElementById("feedCount");

  try {
    const payload = await fetchJson("data/state/urgent-feed.json");
    const feedItems = Array.isArray(payload.items) ? payload.items : [];
    const sorted = feedItems
      .filter((item) => item.complex_id === complexId)
      .filter((item) => Number(item.price_krw) > 0)
      .sort((a, b) => Number(b.alert_planned) - Number(a.alert_planned) || Number(a.price_krw) - Number(b.price_krw))
      .slice(0, 10);

    const overflow = Number(payload.alert_cap_overflow || 0);
    count.textContent = overflow > 0 ? `${sorted.length}건 +${overflow}` : `${sorted.length}건`;
    if (sorted.length === 0) {
      list.replaceChildren(emptyNode("최근 후보 데이터가 아직 없습니다."));
      return;
    }

    list.replaceChildren(...sorted.map(feedItem));
  } catch (error) {
    count.textContent = "오류";
    list.replaceChildren(emptyNode("후보 데이터를 불러오지 못했습니다."));
  }
}

function hasPriceData(history) {
  return history.some((item) =>
    [item.min_price_krw, item.average_price_krw, item.recent_trade_price_krw].some((value) => Number(value) > 0),
  );
}

function drawHistoryChart(canvas, history) {
  const context = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = 44;
  const values = history.flatMap((item) =>
    [item.min_price_krw, item.average_price_krw, item.recent_trade_price_krw].filter((value) => Number(value) > 0),
  );
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);

  context.clearRect(0, 0, width, height);
  context.strokeStyle = "#dce4df";
  context.lineWidth = 1;
  for (let i = 0; i < 5; i += 1) {
    const y = padding + ((height - padding * 2) / 4) * i;
    context.beginPath();
    context.moveTo(padding, y);
    context.lineTo(width - padding, y);
    context.stroke();
  }

  drawSeries(context, history, "min_price_krw", "#16785f", width, height, padding, min, range);
  drawSeries(context, history, "average_price_krw", "#b84f39", width, height, padding, min, range);

  context.fillStyle = "#68736d";
  context.font = "13px Arial";
  context.fillText(`최저 ${currency.format(min)}원`, padding, height - 16);
  context.fillText(`최고 ${currency.format(max)}원`, padding, 24);
}

function drawSeries(context, history, key, color, width, height, padding, min, range) {
  const points = history
    .map((item, index) => ({ value: Number(item[key]), index }))
    .filter((point) => point.value > 0)
    .map((point) => ({
      x: padding + ((width - padding * 2) / Math.max(history.length - 1, 1)) * point.index,
      y: height - padding - ((point.value - min) / range) * (height - padding * 2),
    }));

  if (points.length === 0) {
    return;
  }

  context.strokeStyle = color;
  context.fillStyle = color;
  context.lineWidth = 3;
  context.beginPath();
  points.forEach((point, index) => {
    if (index === 0) {
      context.moveTo(point.x, point.y);
    } else {
      context.lineTo(point.x, point.y);
    }
  });
  context.stroke();

  points.forEach((point) => {
    context.beginPath();
    context.arc(point.x, point.y, 4, 0, Math.PI * 2);
    context.fill();
  });
}

function feedItem(item) {
  const node = document.createElement("article");
  node.className = "feed-item";

  const title = document.createElement("h3");
  title.textContent = item.title || item.description || item.listing_id || "매물";

  const meta = document.createElement("div");
  meta.className = "feed-meta";
  meta.append(
    span(`호가 ${currency.format(Number(item.price_krw || 0))}원`),
    span(`${item.building || "-"}동 / ${item.floor || "-"}층`),
    span(`${item.area_m2 || "-"} m2`),
  );
  if (item.decision_reason) {
    meta.append(span(item.decision_reason));
  }
  if (item.reason) {
    meta.append(span(item.reason));
  }
  if (item.decision) {
    meta.append(span(item.decision));
  }

  node.append(title, meta);
  if (item.link) {
    const link = document.createElement("a");
    link.className = "feed-link";
    link.href = item.link;
    link.rel = "noopener noreferrer";
    link.target = "_blank";
    link.textContent = "매물 열기";
    node.append(link);
  }
  return node;
}

function emptyNode(message) {
  const node = document.createElement("div");
  node.className = "empty-state";
  node.textContent = message;
  return node;
}

function span(text) {
  const node = document.createElement("span");
  node.textContent = text;
  return node;
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path}: ${response.status}`);
  }
  return response.json();
}

function statusLabel(status) {
  if (status === "success") {
    return "정상";
  }
  if (status === "failed") {
    return "실패";
  }
  if (status === "skipped") {
    return "건너뜀";
  }
  return "상태 미확인";
}

function numberOrDash(value) {
  return Number.isFinite(Number(value)) ? currency.format(Number(value)) : "-";
}

function formatTime(value) {
  if (!value || value === "-") {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });
}
