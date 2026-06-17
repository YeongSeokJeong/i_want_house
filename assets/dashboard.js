const COMPLEXES = [
  {
    id: "baengnyeonsan-hillstate-3",
    name: "백련산힐스테이트3차",
    area: "78.87 m2",
    targetPriceKrw: 850000000,
    urgentDiscountRatio: 0.12,
  },
  {
    id: "bulgwang-miseong",
    name: "불광 미성아파트",
    area: "86.47 m2",
    targetPriceKrw: 850000000,
    urgentDiscountRatio: 0.12,
  },
];

const currency = new Intl.NumberFormat("ko-KR");

document.addEventListener("DOMContentLoaded", () => {
  initComplexSelect();
  renderHealth();
  renderDecisionSummary();
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
    renderCollectionDiagnostics(latest);
    await renderMonitoringSummary(latest);
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
    renderCollectionDiagnostics(null, "수집 진단을 불러오지 못했습니다.");
    renderMonitoringSummary(null, "단지별 감시 상태를 불러오지 못했습니다.");
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

async function renderMonitoringSummary(latest, errorMessage) {
  const body = document.getElementById("monitoringSummaryBody");
  const count = document.getElementById("monitoringCount");

  if (errorMessage) {
    count.textContent = "오류";
    body.replaceChildren(monitoringEmptyRow(errorMessage));
    return;
  }

  try {
    const histories = await Promise.all(
      COMPLEXES.map(async (complex) => {
        const payload = await fetchJson(`data/history/${complex.id}.json`);
        return [complex.id, Array.isArray(payload.history) ? payload.history : []];
      }),
    );
    const historyByComplex = Object.fromEntries(histories);
    const diagnostics = diagnosticsByComplex(latest);
    const rows = COMPLEXES.map((complex) =>
      monitoringSummaryRow(complex, latestHistoryEntry(historyByComplex[complex.id] || []), diagnostics[complex.id]),
    );

    count.textContent = `${rows.length}건`;
    body.replaceChildren(...rows);
  } catch (error) {
    count.textContent = "오류";
    body.replaceChildren(monitoringEmptyRow("단지별 감시 상태를 불러오지 못했습니다."));
  }
}

function monitoringSummaryRow(complex, latestHistory, diagnostic) {
  const criteria = criteriaThresholds(complex, latestHistory);
  const minPrice = positiveNumber(latestHistory?.min_price_krw);
  const gapRatio = priceGapRatio(minPrice, criteria.urgentLine);
  const remaining = remainingToUrgentLine(minPrice, criteria.urgentLine);
  const status = monitoringStatus(latestHistory, diagnostic, minPrice, criteria.urgentLine);
  const row = document.createElement("tr");

  row.append(
    tableCell(complex.name, "monitoring-complex"),
    tableCell(complex.area),
    tableCell(formatPrice(complex.targetPriceKrw)),
    tableCell(formatPrice(minPrice)),
    tableCell(formatPrice(positiveNumber(latestHistory?.recent_trade_price_krw))),
    tableCell(formatPrice(criteria.urgentLine)),
    tableCell(criteria.appliedCriterion),
    tableCell(formatRemaining(remaining)),
    tableCell(formatPercent(gapRatio)),
    monitoringStatusCell(status),
  );
  return row;
}

function monitoringEmptyRow(message) {
  const row = document.createElement("tr");
  const cell = tableCell(message);
  cell.colSpan = 10;
  row.append(cell);
  return row;
}

function tableCell(text, className) {
  const cell = document.createElement("td");
  if (className) {
    cell.className = className;
  }
  cell.textContent = text;
  return cell;
}

function monitoringStatusCell(status) {
  const cell = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = `monitoring-status monitoring-status-${status.kind}`;
  badge.textContent = status.label;
  cell.append(badge);
  return cell;
}

function diagnosticsByComplex(latest) {
  const targets = Array.isArray(latest?.listing_diagnostics?.targets) ? latest.listing_diagnostics.targets : [];
  return Object.fromEntries(targets.map((target) => [target.complex_id, target]));
}

function latestHistoryEntry(history) {
  return [...history].sort((a, b) => sortableTime(b.finished_at) - sortableTime(a.finished_at))[0] || null;
}

function urgentLinePrice(complex, latestHistory) {
  return criteriaThresholds(complex, latestHistory).urgentLine;
}

function criteriaThresholds(complex, latestHistory) {
  const targetLine = positiveNumber(complex.targetPriceKrw);
  const tradeBaseline = positiveNumber(latestHistory?.recent_trade_price_krw);
  const discountRatio = Number(complex.urgentDiscountRatio || 0);
  if (!tradeBaseline) {
    return {
      targetLine,
      tradeBaseline: null,
      baselineDiscountLine: null,
      urgentLine: targetLine,
      appliedCriterion: "희망가 상한",
    };
  }
  const baselineDiscountLine = Math.floor(tradeBaseline * (1 - discountRatio));
  const urgentLine = targetLine ? Math.min(targetLine, baselineDiscountLine) : baselineDiscountLine;
  return {
    targetLine,
    tradeBaseline,
    baselineDiscountLine,
    urgentLine,
    appliedCriterion: urgentLine === baselineDiscountLine ? "실거래 할인선" : "희망가 상한",
  };
}

function priceGapRatio(minPrice, urgentLine) {
  if (!minPrice || !urgentLine) {
    return null;
  }
  return ((minPrice - urgentLine) / urgentLine) * 100;
}

function remainingToUrgentLine(minPrice, urgentLine) {
  if (!minPrice || !urgentLine) {
    return null;
  }
  const amount = Math.max(minPrice - urgentLine, 0);
  return {
    amount,
    ratio: (amount / urgentLine) * 100,
    reached: minPrice <= urgentLine,
  };
}

function monitoringStatus(latestHistory, diagnostic, minPrice, urgentLine) {
  if (diagnostic?.status === "empty_response" || Number(latestHistory?.listing_count || 0) === 0) {
    return { kind: "empty", label: "매물 0건" };
  }
  if (!latestHistory) {
    return { kind: "unknown", label: "이력 없음" };
  }
  if (!minPrice || !urgentLine) {
    return { kind: "unknown", label: "기준 부족" };
  }
  const gap = priceGapRatio(minPrice, urgentLine);
  if (gap <= 0) {
    return { kind: "urgent", label: "급매권" };
  }
  if (gap <= 5) {
    return { kind: "near", label: "근접" };
  }
  return { kind: "watch", label: "관망" };
}

function renderCollectionDiagnostics(latest, errorMessage) {
  const list = document.getElementById("collectionDiagnosticsList");
  const count = document.getElementById("diagnosticsCount");
  const targets = Array.isArray(latest?.listing_diagnostics?.targets) ? latest.listing_diagnostics.targets : [];

  if (errorMessage) {
    count.textContent = "오류";
    list.replaceChildren(emptyNode(errorMessage));
    return;
  }

  if (targets.length === 0) {
    count.textContent = "0건";
    list.replaceChildren(emptyNode("최근 실행에 단지별 수집 진단이 없습니다."));
    return;
  }

  count.textContent = `${targets.length}건`;
  list.replaceChildren(...targets.map(collectionDiagnosticItem));
}

function collectionDiagnosticItem(target) {
  const node = document.createElement("article");
  node.className = "diagnostic-item";

  const complex = COMPLEXES.find((item) => item.id === target.complex_id);
  const header = document.createElement("div");
  header.className = "diagnostic-header";

  const title = document.createElement("h3");
  title.textContent = complex?.name || target.complex_id || "단지";

  const status = document.createElement("span");
  status.className = `diagnostic-status diagnostic-status-${target.status || "unknown"}`;
  status.textContent = diagnosticStatusLabel(target.status);

  header.append(title, status);

  const meta = document.createElement("div");
  meta.className = "diagnostic-meta";
  meta.append(span(`매물 ${numberOrDash(target.listing_count)}건`));
  if (target.source_kind) {
    meta.append(span(target.source_kind));
  }
  if (target.source_id) {
    meta.append(span(`source ${target.source_id}`));
  }
  if (target.trade_types) {
    meta.append(span(`tradeTypes ${target.trade_types}`));
  }

  const note = document.createElement("p");
  note.className = "diagnostic-note";
  note.textContent = diagnosticNote(target);

  node.append(header, meta, note);
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

async function renderDecisionSummary() {
  const reasonList = document.getElementById("decisionReasonSummary");
  const complexList = document.getElementById("complexDecisionSummary");
  const count = document.getElementById("decisionSummaryCount");

  try {
    const payload = await fetchJson("data/state/urgent-feed.json");
    const items = Array.isArray(payload.items) ? payload.items : [];
    const summary = decisionSummary(items);
    count.textContent = `${items.length}건`;

    if (items.length === 0) {
      reasonList.replaceChildren(emptyNode("최근 후보 사유가 아직 없습니다."));
      complexList.replaceChildren(...COMPLEXES.map((complex) => complexDecisionItem(complex, null)));
      return;
    }

    reasonList.replaceChildren(...summary.reasons.slice(0, 6).map(reasonSummaryItem));
    complexList.replaceChildren(
      ...COMPLEXES.map((complex) => complexDecisionItem(complex, summary.byComplex[complex.id] || null)),
    );
  } catch (error) {
    count.textContent = "오류";
    reasonList.replaceChildren(emptyNode("탈락/보류 사유를 불러오지 못했습니다."));
    complexList.replaceChildren(emptyNode("단지별 후보 요약을 불러오지 못했습니다."));
  }
}

function decisionSummary(items) {
  const reasonMap = new Map();
  const byComplex = {};

  items.forEach((item) => {
    const decision = item.decision || "unknown";
    const reason = item.reason || "unknown_reason";
    const complexId = item.complex_id || "unknown";
    const key = `${decision}:${reason}`;
    const reasonEntry = reasonMap.get(key) || { decision, reason, count: 0 };
    reasonEntry.count += 1;
    reasonMap.set(key, reasonEntry);

    const complexEntry =
      byComplex[complexId] ||
      {
        total: 0,
        alertPlanned: 0,
        decisions: { approve: 0, hold: 0, reject: 0, unknown: 0 },
        reasons: new Map(),
      };
    complexEntry.total += 1;
    complexEntry.alertPlanned += item.alert_planned ? 1 : 0;
    const decisionKey = ["approve", "hold", "reject"].includes(decision) ? decision : "unknown";
    complexEntry.decisions[decisionKey] += 1;
    const complexReason = complexEntry.reasons.get(key) || { decision, reason, count: 0 };
    complexReason.count += 1;
    complexEntry.reasons.set(key, complexReason);
    byComplex[complexId] = complexEntry;
  });

  Object.values(byComplex).forEach((entry) => {
    entry.reasons = [...entry.reasons.values()].sort(compareReasonEntries);
  });

  return {
    reasons: [...reasonMap.values()].sort(compareReasonEntries),
    byComplex,
  };
}

function compareReasonEntries(a, b) {
  return b.count - a.count || decisionLabel(a.decision).localeCompare(decisionLabel(b.decision), "ko-KR");
}

function reasonSummaryItem(item) {
  const node = document.createElement("article");
  node.className = "reason-summary-item";

  const header = document.createElement("div");
  header.className = "summary-row";
  const title = document.createElement("strong");
  title.textContent = reasonLabel(item.reason);
  const count = document.createElement("span");
  count.textContent = `${item.count}건`;
  header.append(title, count);

  const meta = document.createElement("div");
  meta.className = "summary-meta";
  meta.append(span(decisionLabel(item.decision)), span(item.reason));

  node.append(header, meta);
  return node;
}

function complexDecisionItem(complex, summary) {
  const node = document.createElement("article");
  node.className = "complex-summary-item";

  const header = document.createElement("div");
  header.className = "summary-row";
  const title = document.createElement("strong");
  title.textContent = complex.name;
  const status = document.createElement("span");
  status.textContent = complexSummaryStatus(summary);
  header.append(title, status);

  const meta = document.createElement("div");
  meta.className = "summary-meta";
  if (!summary) {
    meta.append(span("최근 후보 데이터 없음"));
  } else {
    meta.append(
      span(`승인 ${summary.decisions.approve}건`),
      span(`보류 ${summary.decisions.hold}건`),
      span(`탈락 ${summary.decisions.reject}건`),
      span(`알림 ${summary.alertPlanned}건`),
    );
  }

  const reason = document.createElement("p");
  reason.className = "summary-note";
  reason.textContent = complexSummaryReason(summary);

  node.append(header, meta, reason);
  return node;
}

function complexSummaryStatus(summary) {
  if (!summary || summary.total === 0) {
    return "후보 없음";
  }
  if (summary.alertPlanned > 0) {
    return `알림 계획 ${summary.alertPlanned}건`;
  }
  if (summary.decisions.hold > 0 && summary.decisions.reject > 0) {
    return "보류/탈락";
  }
  if (summary.decisions.hold > 0) {
    return "보류";
  }
  if (summary.decisions.reject > 0) {
    return "탈락";
  }
  return "알림 없음";
}

function complexSummaryReason(summary) {
  if (!summary || summary.total === 0) {
    return "최근 feed에 이 단지 후보가 없습니다.";
  }
  const topReasons = summary.reasons
    .slice(0, 3)
    .map((item) => `${reasonLabel(item.reason)} ${item.count}건`)
    .join(" · ");
  return topReasons || "집계할 사유가 없습니다.";
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

function diagnosticStatusLabel(status) {
  if (status === "listings_found") {
    return "매물 확인";
  }
  if (status === "empty_response") {
    return "0건 확인";
  }
  return "미확인";
}

function diagnosticNote(target) {
  if (target.diagnosis === "hogangnono_apt_items_empty") {
    return "호갱노노 매매 API가 정상 응답했지만 매물이 0건입니다.";
  }
  if (target.status === "listings_found") {
    return "매물 source 응답에서 매물이 확인되었습니다.";
  }
  if (target.diagnosis) {
    return target.diagnosis;
  }
  return "수집 진단 세부 정보가 없습니다.";
}

function decisionLabel(value) {
  if (value === "approve") {
    return "승인";
  }
  if (value === "hold") {
    return "보류";
  }
  if (value === "reject") {
    return "탈락";
  }
  return "미확인";
}

function reasonLabel(reason) {
  if (reason === "target_price") {
    return "희망가 기준 통과";
  }
  if (reason === "baseline_price") {
    return "실거래 할인선 통과";
  }
  if (reason === "above_target_price") {
    return "가격 기준 초과";
  }
  if (reason === "already_notified_without_price_drop") {
    return "기존 알림가 이상";
  }
  if (reason?.startsWith("excluded:")) {
    return `제외 키워드: ${reason.slice("excluded:".length)}`;
  }
  if (reason?.startsWith("duplicate_listing:")) {
    return "중복 매물 보류";
  }
  if (reason?.startsWith("average_price_jump")) {
    return "평균가 급변 품질 차단";
  }
  if (reason?.startsWith("llm_")) {
    return `LLM 검수: ${reason.slice("llm_".length)}`;
  }
  return reason || "사유 없음";
}

function numberOrDash(value) {
  return Number.isFinite(Number(value)) ? currency.format(Number(value)) : "-";
}

function positiveNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : null;
}

function formatPrice(value) {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? `${currency.format(number)}원` : "-";
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "-";
  }
  return `${number >= 0 ? "+" : ""}${number.toFixed(1)}%`;
}

function formatRemaining(value) {
  if (!value) {
    return "-";
  }
  if (value.reached) {
    return "도달/초과";
  }
  return `${formatPrice(value.amount)} (${value.ratio.toFixed(1)}%)`;
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
