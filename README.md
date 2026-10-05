# JobSense AI — Understand. Analyze. Prepare.
React + Vite frontend, Flask + SQLite backend, TF-IDF + Logistic Regression job-role model, Gemini for JD analysis.

## Setup (Windows)
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      (then fill in GEMINI_API_KEY, GEMINI_MODEL, SECRET_KEY)
python run.py
```
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. API runs on http://localhost:5000.

## Train the ML model
Put a `.csv`/`.xlsx` job-description dataset in `dataset/`, then from `backend/`:
```
python -m app.ml.train_model
```
It prints the columns, auto-detects the text and role columns (edit the hints in `app/ml/train_model.py` if needed), checks class balance (uses `class_weight="balanced"` only if imbalanced), trains on an 80/20 stratified split, and saves artifacts + real metrics to `backend/app/ml/artifacts/`.
Without a dataset or API key the app still runs and shows clear "unavailable" messages instead of fake results.

## API
`POST /api/auth/register|login`, `GET /api/auth/me`, `GET /api/dashboard/stats`, `POST /api/analyze`, `POST /api/analyze/upload`, `GET /api/analyses`, `GET|DELETE /api/analyses/<id>`, `POST /api/ml/predict`, `GET /api/ml/info`, `GET|PUT /api/profile`.
