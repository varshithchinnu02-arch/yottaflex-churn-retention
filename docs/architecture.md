# Architecture, assumptions and decisions

1. Synthetic generator creates parent Customer and Subscription tables, then monthly usage, billing, support and churn events.
2. Prediction cohort includes customers active at 2025-12-01. Features are computed only from records dated before prediction date.
3. Logistic regression estimates six-month churn probability. Holdout metrics are ROC-AUC, precision, recall and accuracy.
4. Eligibility requires probability >= 0.35 and estimated monthly margin >= 0. Margin is assumed to be 40% of plan price.
5. Eligible customers are randomized 50/50 into treatment/control. Treatment gets OFF-2026-000001; control receives no offer.
6. Treatment retention probability is baseline retention + 12 percentage points (capped at 100%). This is a synthetic simulation assumption, not an observed causal effect.
7. Offer cost is min(10% of monthly plan price x 3 months, USD 8).
8. Campaign lift is treatment retention minus control retention. ROI is an illustrative estimate based on incremental retained customers x three months' plan price less campaign cost.

Limitations: simplified one-subscription-per-customer cohort; no real customer data; no empirical treatment-effect estimation; no confidence intervals or power calculation. Four required anomaly types are recorded in a separate ground_truth.json/ExceptionRegister.csv and flagged for exclusion; the clean base data is not silently corrupted.
