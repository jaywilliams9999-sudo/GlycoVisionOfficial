import { LEVELS, formatDateTime, modelName, parseDate } from "./fields";

// Drawing area in SVG units. The SVG scales to the panel width.
const W = 340;
const H = 170;
const PAD = { top: 10, right: 64, bottom: 26, left: 34 };
const PLOT_W = W - PAD.left - PAD.right;
const PLOT_H = H - PAD.top - PAD.bottom;
const INSET = 10; // keeps the first and last dots inside the plot

const y = (score) => PAD.top + (1 - score) * PLOT_H;
const pct = (score) => Math.round(score * 100);

function axisDate(s, sameDay) {
  const d = parseDate(s);
  return sameDay
    ? d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })
    : d.toLocaleDateString([], { month: "short", day: "numeric" });
}

function ModelChart({ version, points, thresholds, selectedId, onSelect }) {
  // Evenly spaced in date order: visits can be minutes or months apart, and a true
  // time scale would squash same-day assessments into one dot.
  const x = (i) =>
    PAD.left + INSET + (points.length === 1 ? 0 : (i / (points.length - 1)) * (PLOT_W - 2 * INSET));
  const first = points[0].created_at;
  const last = points[points.length - 1].created_at;
  const sameDay = parseDate(first).toDateString() === parseDate(last).toDateString();

  const bands = thresholds && [
    { level: "high", from: 1, to: thresholds.high },
    { level: "moderate", from: thresholds.high, to: thresholds.moderate },
    { level: "low", from: thresholds.moderate, to: 0 },
  ];

  return (
    <figure className="ws-chart">
      <figcaption>
        {modelName(version)} score over time
        <span className="ws-muted"> · {points.length} assessments</span>
      </figcaption>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="group"
        aria-label={`${modelName(version)} model score for each saved assessment, oldest to newest`}
      >
        {bands?.map((b) => (
          <g key={b.level}>
            <rect
              className={`band ${b.level}`}
              x={PAD.left}
              y={y(b.from)}
              width={PLOT_W}
              height={y(b.to) - y(b.from)}
            />
            <text className={`band-label ${b.level}`} x={PAD.left + PLOT_W + 6} y={(y(b.from) + y(b.to)) / 2 + 4}>
              {LEVELS[b.level].replace(" risk", "")}
            </text>
          </g>
        ))}

        {[0, 0.5, 1].map((t) => (
          <g key={t}>
            <line className="grid" x1={PAD.left} x2={PAD.left + PLOT_W} y1={y(t)} y2={y(t)} />
            <text className="tick" x={PAD.left - 6} y={y(t) + 4} textAnchor="end">
              {pct(t)}%
            </text>
          </g>
        ))}

        <polyline className="line" points={points.map((p, i) => `${x(i)},${y(p.risk_probability)}`).join(" ")} />

        {points.map((p, i) => {
          const label = `${formatDateTime(p.created_at)}: ${LEVELS[p.risk_level] ?? p.risk_level}, score ${pct(p.risk_probability)}%`;
          const on = p.id === selectedId;
          return (
            <g
              key={p.id}
              className={`pt ${p.risk_level}${on ? " on" : ""}`}
              role="button"
              tabIndex={0}
              aria-label={`Open result from ${label}`}
              aria-pressed={on}
              onClick={() => onSelect(p)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(p);
                }
              }}
            >
              <title>{label}</title>
              {/* a bigger invisible circle so the dot is easy to click */}
              <circle className="hit" cx={x(i)} cy={y(p.risk_probability)} r={11} />
              <circle className="dot" cx={x(i)} cy={y(p.risk_probability)} r={on ? 6.5 : 5} />
            </g>
          );
        })}

        <text className="tick" x={x(0)} y={H - 6} textAnchor={points.length === 1 ? "middle" : "start"}>
          {axisDate(first, sameDay)}
        </text>
        {points.length > 1 && (
          <text className="tick" x={x(points.length - 1)} y={H - 6} textAnchor="end">
            {axisDate(last, sameDay)}
          </text>
        )}
      </svg>
    </figure>
  );
}

/**
 * One line graph per model: scores from different models can't be compared, so
 * they never share an axis. Shown once a model has two or more saved results.
 * history: the patient's assessments, oldest first (as the API returns them).
 */
export default function RiskChart({ history, modelsByVersion, selectedId, onSelect }) {
  const byModel = new Map();
  for (const a of history) {
    if (!byModel.has(a.model_version)) byModel.set(a.model_version, []);
    byModel.get(a.model_version).push(a);
  }
  const charts = [...byModel].filter(([, points]) => points.length >= 2);
  if (charts.length === 0) return null;

  return (
    <div className="ws-charts">
      {charts.map(([version, points]) => (
        <ModelChart
          key={version}
          version={version}
          points={points}
          thresholds={modelsByVersion[version]?.risk_thresholds}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
      <p className="ws-hint">Points are in date order, evenly spaced. Select one to open that result.</p>
    </div>
  );
}
