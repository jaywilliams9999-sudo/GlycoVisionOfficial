import { LEVELS, displayValue, formatDateTime, labelFor, modelName } from "./fields";

function Result({ a, model }) {
  const pct = Math.round(a.risk_probability * 100);

  const drivers = a.shap_values.filter((c) => Math.abs(c.contribution) >= 0.0005).slice(0, 8);
  const max = Math.max(...drivers.map((c) => Math.abs(c.contribution)), 0.0001);

  return (
    <div>
      <h2>Result</h2>
      <p className="ws-meta">
        {formatDateTime(a.created_at)} · {modelName(a.model_version)} model ({a.model_version})
      </p>

      <div className={`ws-headline ${a.risk_level}`}>
        <strong>{LEVELS[a.risk_level] ?? a.risk_level}</strong>
        <span>Model score {pct}%</span>
      </div>
      <div
        className="ws-meter"
        role="img"
        aria-label={`Model score ${pct} percent, ${LEVELS[a.risk_level] ?? a.risk_level}`}
      >
        <i className={a.risk_level} style={{ width: `${Math.max(2, pct)}%` }} />
      </div>

      {drivers.length > 0 && (
        <>
          <h3>What moved the score</h3>
          <ul className="ws-drivers">
            {drivers.map((c) => {
              const up = c.contribution > 0;
              const width = `${(Math.abs(c.contribution) / max) * 100}%`;
              return (
                <li key={c.feature}>
                  <div className="ws-driver-top">
                    <span>{labelFor(c.feature)}</span>
                    <span className="ws-muted">
                      {displayValue(c.feature, c.value, model?.inputs?.[c.feature])}
                    </span>
                  </div>
                  <div className="ws-dv-row">
                    <div className="ws-dv" aria-hidden="true">
                      <span className="neg">{!up && <i style={{ width }} />}</span>
                      <span className="pos">{up && <i style={{ width }} />}</span>
                    </div>
                    <span className={`ws-dir ${up ? "up" : "down"}`}>
                      {up ? "Raises" : "Lowers"}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
          <p className="ws-hint">
            Bars show how much each answer pushed the score up or down from the model's average.
          </p>
        </>
      )}

      <p className="ws-disclaimer">
        Decision support only. The score is a model output, not a diagnosis, and may not match a
        patient's real-world chance of diabetes.
      </p>
    </div>
  );
}

function Timeline({ history, selectedId, onSelect, error }) {
  const rows = [...history].reverse(); 
  const mixed = new Set(history.map((h) => h.model_version)).size > 1;
  return (
    <div className="ws-timeline">
      <h3>Risk timeline</h3>
      {error && (
        <p className="ws-err" role="alert">
          {error}
        </p>
      )}
      {!error && rows.length === 0 && (
        <p className="ws-muted">No assessments yet for this patient.</p>
      )}
      {rows.length > 0 && (
        <ul>
          {rows.map((h) => (
            <li key={h.id}>
              <button
                type="button"
                aria-pressed={h.id === selectedId}
                className={h.id === selectedId ? "on" : ""}
                onClick={() => onSelect(h)}
              >
                <span className="when">{formatDateTime(h.created_at)}</span>
                <span className="what">{modelName(h.model_version)}</span>
                <span className={`ws-pill ${h.risk_level}`}>
                  {LEVELS[h.risk_level] ?? h.risk_level} · {Math.round(h.risk_probability * 100)}%
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {mixed && (
        <p className="ws-hint">Scores from different models can't be compared with each other.</p>
      )}
    </div>
  );
}

export default function ResultsPanel({ shown, history, modelsByVersion, onSelect, historyError }) {
  return (
    <aside className="ws-card ws-results" aria-live="polite">
      {shown ? (
        <Result a={shown} model={modelsByVersion[shown.model_version]} />
      ) : (
        <div>
          <h2>Result</h2>
          <p className="ws-muted">
            Enter the patient's values and select Calculate and save risk. Past results are listed
            below.
          </p>
        </div>
      )}
      <Timeline
        history={history}
        selectedId={shown?.id}
        onSelect={onSelect}
        error={historyError}
      />
    </aside>
  );
}
