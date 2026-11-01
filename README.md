# GlycoVision

**Explainable Type 2 diabetes risk assessment for clinicians.**

GlycoVision takes a patient's biomarkers and returns a risk score with a color-coded risk level (low, moderate or high). It uses [SHAP](https://github.com/shap/shap) to show how much each input pushed the prediction up or down, so a clinician can see *why* a patient was flagged, not just that they were. Assessments are saved per patient, so changes in risk can be followed over time on the Risk Timeline.

## Features

- **Two models, one interface.** A clinical model for patients with lab values and a screening model for survey-style data (see [Models](#models)). The frontend builds its input form from each model's metadata.
- **Per-input explanations.** Every result lists each input's SHAP contribution, largest first. Missing-value indicators are folded back into the input they belong to, so there is one bar per value the clinician entered.
- **Optional lab values.** Some inputs can be left blank when not measured; the model imputes them.
- **Patient records and Risk Timeline.** Each clinician manages their own patients and can review every past assessment for a patient.
- **Clinician-only access.** Login with a signed token, account lockout after 5 failed attempts, and the same error message for a wrong username or password. There is no sign-up page on purpose: accounts are created by an admin (see [Managing clinician accounts](#managing-clinician-accounts)).
- **Strict input validation.** The API rejects any input outside the ranges defined in the model's metadata.

## Models

Both models share the same risk thresholds: **moderate at 0.33** and **high at 0.66** predicted probability.

| Model | Version | Data | Inputs | ROC AUC | Recall |
|---|---|---|---|---|---|
| Clinical | `clinical-v1` | Pima Indians Diabetes dataset (768 rows) | 8 (glucose, BMI, age, insulin, ...) | 0.827 | 0.741 |
| Screening | `screening-v1` | CDC BRFSS survey data (253,680 rows) | 17 (blood pressure, general health, activity, ...) | 0.820 | 0.782 |

Metrics are from a held-out 20% test split. Each model lives in `models/<version>/` as a `model.joblib` plus a `metadata.json` (features, valid ranges, metrics, thresholds, training config). These files are committed on purpose, so the API runs without retraining.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy (SQLite by default), Pydantic, bcrypt, PyJWT |
| ML | scikit-learn 1.9.1, SHAP 0.52.0, pandas, joblib |
| Frontend | React 19, TypeScript, Vite |
| Tests | pytest, httpx |

## Project structure

```
backend/     FastAPI app (api/ -> services/ -> repositories/, plus ml/ for models and SHAP)
  scripts/   Admin tools (clinician accounts)
  tests/     API and auth tests
frontend/    React + Vite app; all backend calls go through src/api/client.ts
models/      Trained model stores (model.joblib + metadata.json), committed
training/    Config-driven training pipeline (configs/, steps/, run_training.py)
```

## Getting started

You'll need Python 3 and Node.js.

### 1. Backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

cd backend
python -m scripts.clinicians add <username> "<Full Name>"   # create a login (prompts for a password)
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`, with interactive docs at `/docs`. The SQLite database is created on first run at `backend/glycovision.db` (git-ignored).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/*` to the backend on port 8000.

### 3. Run the tests

```bash
cd backend
pytest
```

## Configuration

The backend reads these environment variables. The defaults are for local development only.

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | dev-only placeholder | Signs login tokens. **Set a long random value outside development.** |
| `DATABASE_URL` | SQLite file in `backend/` | Database connection |
| `MODEL_DIR` | `models/` in the repo root | Where model stores are loaded from |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `TOKEN_MINUTES` | `30` | Login token lifetime |

Generate a secret with `python -c "import secrets; print(secrets.token_hex(32))"`.

## API overview

All routes except `/auth/login` and `/models` require a logged-in clinician.

| Method | Route | Description |
|---|---|---|
| `POST` | `/auth/login` | Returns a token. 401 for bad credentials, 423 if locked |
| `GET` | `/models` | Each model's features and valid input ranges |
| `POST` / `GET` | `/patients` | Create or list your patients |
| `GET` | `/patients/{id}` | One patient |
| `GET` | `/patients/{id}/assessments` | The Risk Timeline |
| `POST` | `/assessments` | Score, explain and save an assessment |
| `GET` | `/assessments/{id}` | One saved assessment |

## Managing clinician accounts

Run from `backend/` with the venv active:

```bash
python -m scripts.clinicians add <username> "<Full Name>"
python -m scripts.clinicians unlock <username>      # reset a locked account
```

## Retraining the models

Training is driven by a YAML config. Run it from `training/`:

```bash
cd training
pip install -r requirements.txt
python scripts/download_data.py                  # downloads and verifies the raw datasets
python run_training.py configs/clinical.yaml     # or configs/screening.yaml
```

**Always pass a config file**, or training won't run. The new model is written to `models/<model_version>/`. The backend refuses to start if a model was trained with a different scikit-learn version than the one installed, so keep `scikit-learn` pinned to the same version in both `requirements.txt` files. Raw data in `data/` is git-ignored; the `models/` folder is not.

## Contributing

All work happens on a short-lived branch and reaches `main` through a reviewed pull request.

### 1. Start from an up-to-date `main`

```bash
git checkout main
git pull
```

This way your branch starts from the latest code, not from last week's.

### 2. Create a branch for one task

```bash
git checkout -b feature/risk-timeline-chart
```

- `-b` creates the branch and switches to it in one step.
- Name branches after what they do: `feature/...` for new work, `fix/...` for bug fixes, `docs/...` for documentation.
- One branch per task. Small branches are easier to review and less likely to conflict.

### 3. Do your work and commit as you go

```bash
git status
git add backend/app/api/assessments.py
git commit -m "Return SHAP contributions from the assessments endpoint"
```

Commit whenever a small piece works. Several small commits are easier to follow than one huge one.

### 4. Push the branch to GitHub

```bash
git push -u origin feature/risk-timeline-chart
```

- `-u` links your local branch to the one on GitHub. After that first push, plain `git push` works.
- Pushing a branch doesn't touch `main`, so it's safe to push unfinished work as a backup.

### 5. Open the pull request

1. Go to the repo on GitHub. A yellow banner usually appears saying the branch had recent pushes. Click **Compare & pull request**.
   - If the banner isn't there: **Pull requests** tab → **New pull request** → set base to `main` and compare to your branch.
2. Write a clear title, like "Add SHAP explanations to /assessments".
3. In the description, cover:
   - **What** changed
   - **Why** it changed
   - **How to test it**, for example: "Run `uvicorn app.main:app --reload`, POST to `/assessments`, check the `shap_values` field."
4. Add a groupmate as a **Reviewer** using the right sidebar.
5. Click **Create pull request**.

### 6. Review

- The reviewer opens the **Files changed** tab, leaves comments on specific lines, then chooses **Approve** or **Request changes**.
- To fix something they flagged, commit to the same branch and push again. The PR updates automatically, so you never need to open a new one.

### 7. Merge

- Once it's approved, click **Merge pull request** on GitHub.
- GitHub then offers to **Delete branch**. Accept it, since the work is now in `main`.

### 8. Clean up locally and start the next task

```bash
git checkout main
git pull
git branch -d feature/risk-timeline-chart
```

Then go back to step 2 for the next task.

## License

[MIT](LICENSE)