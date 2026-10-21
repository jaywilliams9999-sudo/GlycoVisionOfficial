import { useRef, useState } from "react";
import { createAssessment } from "./api";
import { HINTS, MODEL_INFO, UNITS, choicesFor, defaultsFor, labelFor, modelName } from "./fields";

function validate(model, values) {
  const errors = {};
  for (const f of model.features) {
    const spec = model.inputs[f];
    const raw = values[f] ?? "";
    if (raw === "") {
      if (!spec.optional) errors[f] = choicesFor(f, spec) ? "Select an answer." : "Enter a value.";
      continue;
    }
    const n = Number(raw);
    if (!Number.isFinite(n) || n < spec.min || n > spec.max) {
      errors[f] = `Enter a value from ${spec.min} to ${spec.max}.`;
    }
  }
  return errors;
}

function Field({ id, spec, choices, value, error, onChange }) {
  const hint = [HINTS[id], choices ? "" : `Valid range ${spec.min} to ${spec.max}.`]
    .filter(Boolean)
    .join(" ");
  const common = {
    id: `f-${id}`,
    value,
    onChange,
    "aria-invalid": !!error,
    "aria-describedby": error ? `f-${id}-e` : undefined,
  };
  return (
    <div className="ws-field">
      <label htmlFor={`f-${id}`}>
        {labelFor(id)}
        {UNITS[id] && <span className="ws-unit"> {UNITS[id]}</span>}
        {spec.optional && <span className="ws-unit"> (optional)</span>}
      </label>
      {choices ? (
        <select {...common}>
          <option value="">Select</option>
          {choices.map(([v, text]) => (
            <option key={v} value={v}>
              {text}
            </option>
          ))}
        </select>
      ) : (
        <input {...common} type="number" step="any" inputMode="decimal" />
      )}
      {error ? (
        <p className="ws-err" id={`f-${id}-e`}>
          {error}
        </p>
      ) : (
        hint && <p className="ws-hint">{hint}</p>
      )}
    </div>
  );
}

export default function AssessmentForm({ token, patient, models, onResult }) {
  const [version, setVersion] = useState(models[0].model_version);
  const [values, setValues] = useState(() => defaultsFor(patient));
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle");
  const [apiError, setApiError] = useState("");
  const formRef = useRef(null);

  const model = models.find((m) => m.model_version === version);
  const fields = model.features.map((id) => ({
    id,
    spec: model.inputs[id],
    choices: choicesFor(id, model.inputs[id]),
  }));
  const groups = [
    { title: "Measurements", items: fields.filter((f) => !f.choices) },
    { title: "History and lifestyle", items: fields.filter((f) => f.choices) },
  ].filter((g) => g.items.length > 0);

  const set = (id) => (e) => {
    setValues((s) => ({ ...s, [id]: e.target.value }));
    if (errors[id]) setErrors((s) => ({ ...s, [id]: undefined }));
  };

  function chooseModel(v) {
    setVersion(v);
    setErrors({});
    setApiError("");
    setStatus("idle");
  }

  async function onSubmit(e) {
    e.preventDefault();
    if (status === "saving") return;
    const errs = validate(model, values);
    setErrors(errs);
    if (Object.keys(errs).length) {
      setTimeout(() => formRef.current?.querySelector('[aria-invalid="true"]')?.focus(), 0);
      return;
    }
    
    const inputs = Object.fromEntries(
      model.features.map((f) => [f, (values[f] ?? "") === "" ? null : Number(values[f])])
    );
    setStatus("saving");
    setApiError("");
    try {
      const assessment = await createAssessment(token, {
        patient_id: patient.id,
        model_version: version,
        inputs,
      });
      setStatus("idle");
      onResult(assessment);
    } catch (err) {
      setApiError(err.message);
      setStatus("error");
    }
  }

  return (
    <form className="ws-form" onSubmit={onSubmit} noValidate ref={formRef}>
      {models.length > 1 && (
        <fieldset>
          <legend>Model</legend>
          <div className="ws-models">
            {models.map((m) => (
              <label className="ws-model" key={m.model_version}>
                <input
                  type="radio"
                  name="model"
                  value={m.model_version}
                  checked={m.model_version === version}
                  onChange={() => chooseModel(m.model_version)}
                />
                <span>
                  <strong>{modelName(m.model_version)}</strong>
                  <small>{MODEL_INFO[m.model_version]?.blurb ?? m.model_version}</small>
                </span>
              </label>
            ))}
          </div>
        </fieldset>
      )}

      {groups.map((g) => (
        <fieldset key={g.title}>
          <legend>{g.title}</legend>
          <div className="ws-row">
            {g.items.map((f) => (
              <Field
                key={`${version}-${f.id}`}
                id={f.id}
                spec={f.spec}
                choices={f.choices}
                value={values[f.id] ?? ""}
                error={errors[f.id]}
                onChange={set(f.id)}
              />
            ))}
          </div>
        </fieldset>
      ))}

      <p className="ws-hint">
        Optional fields can be left blank if they weren't measured. The model fills in a typical
        value for them.
      </p>

      {status === "error" && (
        <div className="ws-alert" role="alert">
          <strong>Couldn't calculate risk</strong>
          <p>{apiError}</p>
        </div>
      )}

      <div className="ws-actions">
        <button type="submit" className="ws-primary" disabled={status === "saving"}>
          {status === "saving" ? "Calculating…" : "Calculate and save risk"}
        </button>
        <button
          type="button"
          className="ws-ghost"
          onClick={() => {
            setValues(defaultsFor(patient));
            setErrors({});
            setApiError("");
            setStatus("idle");
          }}
        >
          Clear form
        </button>
      </div>
      <p className="ws-hint">Each calculation is saved to this patient's record.</p>
    </form>
  );
}
