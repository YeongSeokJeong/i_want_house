const COMPLEXES = [
  { id: "baengnyeonsan-hillstate-3", name: "백련산힐스테이트3차", area: "78.87 m2" },
  { id: "bulgwang-miseong", name: "불광 미성아파트", area: "86.47 m2" },
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
    renderRunHistory(health);
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
    renderRunHistory(null, "수집/검색 이력을 불러오지 못했습니다.");
  }
}

function renderRunHistory(health, errorMessage) {
  const list = document.getElementById("runHistoryList");
  const count = document.getElementById("runHistoryCount");
  const runs = Array.isArray(health?.runs) ? [...health.runs] : [];

  if (errorMessage) {
    count.textContent = "오류";
    list.replaceChildren(emptyNode(errorMessage));
    return;
  }

  if (runs.length === 0) {
    count.textContent = "0건";
    list.replaceChildren(emptyNode("수집/검색 실행 이력이 아직 없습니다."));
    return;
  }

  const sorted = runs
    .sort((a, b) => sortableTime(b.finished_at || b.started_at) - sortableTime(a.finished_at || a.started_at))
    .slice(0, 8);
  count.textContent = `${runs.length}건`;
  list.replaceChildren(...sorted.map(runHistoryItem));
}

function runHistoryItem(run) {
  const node = document.createElement("article");
  node.className = "run-history-item";

  const header = document.createElement("div");
  header.className = "run-history-header";

  const title = document.createElement("div");
  title.className = "run-history-title";
  title.textContent = formatTime(run.finished_at || run.started_at || "-");

  const status = document.createElement("span");
  status.className = `run-status run-status-${run.status || "unknown"}`;
  status.textContent = statusLabel(run.status);

  header.append(title, status);

  const meta = document.createElement("div");
  meta.className = "run-history-meta";
  if (run.run_id) {
    meta.append(span(`run ${shortRunId(run.run_id)}`));
  }
  if (run.reason) {
    meta.append(span(run.reason));
  }

  const counts = run.counts || {};
  const metrics = document.createElement("div");
  metrics.className = "run-history-metrics";
  metrics.append(
    metricPill("감시", counts.watched_complexes),
    metricPill("정상", counts.valid_listings),
    metricPill("후보", counts.approved_candidates),
    metricPill("알림", counts.notifications_sent),
  );

  node.append(header, meta, metrics);
  return node;
}

function metricPill(label, value) {
  const node = document.createElement("span");
  node.textContent = `${label} ${numberOrDash(value)}`;
  return node;
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
  const summary = document.getElementById("historySummary");

  try {
    const payload = await fetchJson(`data/history/${complexId}.json`);
    const history = Array.isArray(payload.history) ? payload.history : [];
    renderHistorySummary(history, summary);
    if (history.length === 0 || !hasPriceData(history)) {
      canvas.hidden = true;
      empty.hidden = false;
      empty.textContent =
        history.length === 0
          ? "히스토리 데이터가 아직 없습니다."
          : "수집 이력은 있지만 표시할 가격 데이터가 아직 없습니다.";
      return;
    }
    empty.hidden = true;
    canvas.hidden = false;
    drawHistoryChart(canvas, history);
  } catch (error) {
    canvas.hidden = true;
    empty.hidden = false;
    empty.textContent = "히스토리 데이터를 불러오지 못했습니다.";
    summary.textContent = "단지 이력을 불러오지 못했습니다.";
  }
}

function renderHistorySummary(history, target) {
  if (history.length === 0) {
    target.textContent = "아직 이 단지의 수집 이력이 없습니다.";
    return;
  }

  const latest = [...history].sort((a, b) => sortableTime(b.finished_at) - sortableTime(a.finished_at))[0];
  const totalListings = history.reduce((sum, item) => sum + Number(item.listing_count || 0), 0);
  const latestListingCount = Number(latest.listing_count || 0);
  const latestTime = formatTime(latest.finished_at || "-");

  if (!hasPriceData(history)) {
    target.textContent =
      totalListings === 0
        ? `최근 ${history.length}번 수집에서 매매 매물이 0건으로 기록되었습니다.`
        : `최근 수집(${latestTime}) 기준 매물 ${latestListingCount}건이 기록됐지만 가격 집계가 없습니다.`;
    return;
  }

  const parts = [`최근 수집 ${latestTime}`, `매물 ${latestListingCount}건`];
  if (Number(latest.min_price_krw) > 0) {
    parts.push(`최저 호가 ${formatPrice(latest.min_price_krw)}`);
  }
  if (Number(latest.average_price_krw) > 0) {
    parts.push(`평균 호가 ${formatPrice(latest.average_price_krw)}`);
  }
  if (Number(latest.recent_trade_price_krw) > 0) {
    parts.push(`실거래 기준선 ${formatPrice(latest.recent_trade_price_krw)}`);
  }
  target.textContent = parts.join(" · ");
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
  context.setLineDash([]);
  for (let i = 0; i < 5; i += 1) {
    const y = padding + ((height - padding * 2) / 4) * i;
    context.beginPath();
    context.moveTo(padding, y);
    context.lineTo(width - padding, y);
    context.stroke();
  }

  drawSeries(context, history, "min_price_krw", "#16785f", width, height, padding, min, range);
  drawSeries(context, history, "average_price_krw", "#b84f39", width, height, padding, min, range);
  drawSeries(context, history, "recent_trade_price_krw", "#4b5fc0", width, height, padding, min, range, [8, 6]);

  context.fillStyle = "#68736d";
  context.font = "13px Arial";
  context.fillText(`최저 ${formatPrice(min)}`, padding, height - 16);
  context.fillText(`최고 ${formatPrice(max)}`, padding, 24);
}

function drawSeries(context, history, key, color, width, height, padding, min, range, dash = []) {
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
  context.setLineDash(dash);
  context.beginPath();
  points.forEach((point, index) => {
    if (index === 0) {
      context.moveTo(point.x, point.y);
    } else {
      context.lineTo(point.x, point.y);
    }
  });
  context.stroke();
  context.setLineDash([]);

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
    span(`호가 ${formatPrice(Number(item.price_krw || 0))}`),
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

function formatPrice(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${currency.format(number)}원` : "-";
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

function sortableTime(value) {
  const timestamp = new Date(value || 0).getTime();
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function shortRunId(value) {
  return String(value).length > 12 ? `${String(value).slice(0, 12)}...` : String(value);
}
