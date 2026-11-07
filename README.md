# YottaFlex AI — Churn Prediction & Retention Offer Simulator

End-to-end local prototype using fully synthetic data. It generates linked customer/subscription/event histories, builds pre-prediction features, trains a churn model, applies eligibility/margin rules, randomizes campaign groups and measures simulated outcomes.


## Run on Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.generate --customers 20000 --seed 20261022
.\.venv\Scripts\python.exe -m src.model
.\.venv\Scripts\python.exe -c "from src.campaign import simulate,metrics; d=simulate(); print(metrics(d))"
.\.venv\Scripts\python.exe -m src.validate
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```


## Core definitions
- Prediction date: 2025-12-01.
- Prediction horizon: six months, 2026-01-01 to 2026-06-30.
- Feature cutoff: strictly before prediction date.
- Churn label: churn event during the six-month horizon.
- Eligibility: churn probability >= 0.35 and estimated monthly margin >= 0.
- Assignment: randomized 50/50 treatment/control among eligible customers.
- Offer: 10% monthly discount for 3 months; simulated cost capped at USD 8.
- Outcome: synthetic retention with treatment uplift assumption +12 percentage points, capped at 100%.

## Metrics
ROC-AUC, precision, recall, accuracy, observed cohort churn rate, treatment/control retention, incremental lift, campaign cost, estimated incremental retained customers and illustrative ROI.

## Reproducibility and provenance
Default seed 20261022. All data is synthetic; no external source is used. Run generator twice with same scale/seed and compare checksums to demonstrate deterministic generation:
```powershell
Get-FileHash data/generated/Customer.csv -Algorithm SHA256
```
Store checksums in your submission notes. The generated files are not committed by default; regenerate them using the command above.

## Tests
```powershell
pytest -q
python -m src.validate
```

## Public GitHub repository
```powershell
git init
git add .
git commit -m "Build churn prediction and retention offer simulator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/yottaflex-churn-retention.git
git push -u origin main
```
Create the repository as **Public** on GitHub first. Replace YOUR_USERNAME. Do not upload secrets, private data, virtual environments or unnecessarily large generated CSVs.

## Honest limitations
This is a synthetic decision-support demonstration, not a production churn service. Campaign uplift and outcomes are simulated using a stated assumption; they are not evidence of real-world incremental lift. For production, add confidence intervals, power analysis, multiple subscriptions, a proper customer-offer bridge, event-sourced lifecycle tables and stronger audit controls.
