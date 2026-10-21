import { useCallback, useEffect, useMemo, useState } from "react";
import "./workspace.css";
import { createPatient, listAssessments, listModels, listPatients } from "./api";
import { ageFromDob, formatDob } from "./fields";
import AssessmentForm from "./AssessmentForm";
import ResultsPanel from "./Results";

const todayString = () => new Date().toLocaleDateString("en-CA");
const MAX_SHOWN = 50;

function PatientPicker({ token, onPick }) {
  const [patients, setPatients] = useState(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [dob, setDob] = useState("");
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [createError, setCreateError] = useState("");

  const load = useCallback(() => {
    setError("");
    listPatients(token)
      .then(setPatients)
      .catch((e) => setError(e.message));
  }, [token]);
  useEffect(() => {
    load();
  }, [load]);

  const q = query.trim().toLowerCase();
  const matches = (patients ?? []).filter((p) => p.identifier.toLowerCase().includes(q));

  async function create(e) {
    e.preventDefault();
    const id = identifier.trim();
    const errs = {};
    if (!id) errs.identifier = "Enter the patient's MRN.";
    else if ((patients ?? []).some((p) => p.identifier.toLowerCase() === id.toLowerCase())) {
      errs.identifier = "A patient with this MRN already exists. Find them in the list.";
    }
    if (!dob) errs.dob = "Enter the date of birth.";
    else if (dob > todayString()) errs.dob = "Date of birth can't be in the future.";
    else if (ageFromDob(dob) < 18) errs.dob = "These models are for patients 18 and older.";
    else if (ageFromDob(dob) > 120) errs.dob = "Check the date of birth.";
    setErrors(errs);
    if (Object.keys(errs).length) return;

    setSaving(true);
    setCreateError("");
    try {
      onPick(await createPatient(token, { identifier: id, date_of_birth: dob }));
    } catch (err) {
      setCreateError(err.message);
      setSaving(false);
    }
  }

  return (
    <div className="ws-picker">
      <section className="ws-card">
        <h2>Find a patient</h2>
        <label htmlFor="search">Search by MRN</label>
        <input
          id="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        {error && (
          <div className="ws-alert" role="alert">
            <strong>Couldn't load patients</strong>
            <p>{error}</p>
            <button type="button" className="ws-ghost" onClick={load}>
              Try again
            </button>
          </div>
        )}
        {!error && patients === null && <p className="ws-muted">Loading patients…</p>}
        {patients && matches.length === 0 && (
          <p className="ws-muted">
            {patients.length === 0
              ? "No patients yet. Add the first one."
              : "No patient matches that MRN."}
          </p>
        )}
        {matches.length > 0 && (
          <ul className="ws-plist">
            {matches.slice(0, MAX_SHOWN).map((p) => (
              <li key={p.id}>
                <button type="button" onClick={() => onPick(p)}>
                  <strong>{p.identifier}</strong>
                  <span>Born {formatDob(p.date_of_birth)}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
        {matches.length > MAX_SHOWN && (
          <p className="ws-hint">Showing the first {MAX_SHOWN}. Search to narrow the list.</p>
        )}
      </section>

      <form className="ws-card" onSubmit={create} noValidate>
        <h2>Add a new patient</h2>
        <label htmlFor="mrn">MRN</label>
        <input
          id="mrn"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          maxLength={64}
          autoComplete="off"
          aria-invalid={!!errors.identifier}
        />
        {errors.identifier && <p className="ws-err">{errors.identifier}</p>}

        <label htmlFor="dob">Date of birth</label>
        <input
          id="dob"
          type="date"
          value={dob}
          max={todayString()}
          onChange={(e) => setDob(e.target.value)}
          aria-invalid={!!errors.dob}
        />
        {errors.dob && <p className="ws-err">{errors.dob}</p>}

        {createError && (
          <div className="ws-alert" role="alert">
            <strong>Couldn't add the patient</strong>
            <p>{createError}</p>
          </div>
        )}
        <button type="submit" className="ws-primary" disabled={saving}>
          {saving ? "Adding…" : "Add patient and continue"}
        </button>
      </form>
    </div>
  );
}

export default function Workspace({ token }) {
  const [models, setModels] = useState(null);
  const [modelsError, setModelsError] = useState("");
  const [patient, setPatient] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState("");
  const [shown, setShown] = useState(null);

  const loadModels = useCallback(() => {
    setModelsError("");
    listModels(token)
      .then(setModels)
      .catch((e) => setModelsError(e.message));
  }, [token]);
  useEffect(() => {
    loadModels();
  }, [loadModels]);

  useEffect(() => {
    if (!patient) return undefined;
    let cancelled = false;
    setHistory([]);
    setShown(null);
    setHistoryError("");
    listAssessments(token, patient.id)
      .then((h) => !cancelled && setHistory(h))
      .catch((e) => !cancelled && setHistoryError(e.message));
    return () => {
      cancelled = true;
    };
  }, [patient, token]);

  const modelsByVersion = useMemo(
    () => Object.fromEntries((models ?? []).map((m) => [m.model_version, m])),
    [models]
  );

  let body;
  if (modelsError) {
    body = (
      <div className="ws-alert ws-card" role="alert">
        <strong>Couldn't load the models</strong>
        <p>{modelsError}</p>
        <button type="button" className="ws-ghost" onClick={loadModels}>
          Try again
        </button>
      </div>
    );
  } else if (!models) {
    body = <p className="ws-muted">Loading…</p>;
  } else if (!patient) {
    body = <PatientPicker token={token} onPick={setPatient} />;
  } else {
    body = (
      <>
        <div className="ws-patient">
          <div>
            <strong>{patient.identifier}</strong>
            <span>
              Born {formatDob(patient.date_of_birth)} · {ageFromDob(patient.date_of_birth)} years
            </span>
          </div>
          <button type="button" className="ws-ghost" onClick={() => setPatient(null)}>
            Change patient
          </button>
        </div>
        <div className="ws-grid">
          <AssessmentForm
            key={patient.id}
            token={token}
            patient={patient}
            models={models}
            onResult={(a) => {
              setShown(a);
              setHistory((h) => [...h, a]);
              
              if (window.matchMedia("(max-width: 900px)").matches) {
                setTimeout(
                  () => document.querySelector(".ws-results")?.scrollIntoView({ block: "start" }),
                  0
                );
              }
            }}
          />
          <ResultsPanel
            shown={shown}
            history={history}
            modelsByVersion={modelsByVersion}
            onSelect={setShown}
            historyError={historyError}
          />
        </div>
      </>
    );
  }

  return (
    <div className="ws">
      <div className="ws-wrap">
        <header className="ws-head">
          <h1>Diabetes risk assessment</h1>
          <p>{patient ? "Enter the patient's latest values." : "Choose a patient to begin."}</p>
        </header>
        {body}
      </div>
    </div>
  );
}
