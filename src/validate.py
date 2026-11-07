from pathlib import Path
import pandas as pd,json
def validate(data_dir="data/generated"):
 p=Path(data_dir)
 C=pd.read_csv(p/"Customer.csv"); S=pd.read_csv(p/"Subscription.csv"); U=pd.read_csv(p/"UsageSnapshot.csv")
 B=pd.read_csv(p/"BillingEvent.csv"); K=pd.read_csv(p/"SupportCase.csv"); F=pd.read_csv(p/"PredictionFeatures.csv")
 checks={
 "customer_pk_unique":C.customer_id.is_unique,"subscription_pk_unique":S.subscription_id.is_unique,
 "usage_pk_unique":U.snapshot_id.is_unique,"billing_pk_unique":B.billing_event_id.is_unique,
 "support_pk_unique":K.support_case_id.is_unique,"subscription_customer_fk":S.customer_id.isin(C.customer_id).all(),
 "usage_subscription_fk":U.subscription_id.isin(S.subscription_id).all(),"billing_subscription_fk":B.subscription_id.isin(S.subscription_id).all(),
 "support_customer_fk":K.customer_id.isin(C.customer_id).all(),"nonnegative_usage":(U.usage_units>=0).all(),
 "nonnegative_billing":(B.amount_due>=0).all() and (B.overdue_amount>=0).all(),
 "binary_labels":F.churn_label.isin([0,1]).all(),"one_feature_row_per_customer":F.customer_id.is_unique,
 "features_prediction_date":(pd.to_datetime(F.prediction_date)==pd.Timestamp("2025-12-01")).all(),
 "ground_truth_separate":(p/"ground_truth.json").exists()}
 return {"passed":bool(all(checks.values())),"checks":{k:bool(v) for k,v in checks.items()},
  "rows":{"customers":len(C),"subscriptions":len(S),"usage":len(U),"billing":len(B),"support":len(K),"cohort":len(F)},
  "anomalies":len(json.loads((p/"ground_truth.json").read_text()).get("anomalies",[]))}
if __name__=="__main__":
 import json; print(json.dumps(validate(),indent=2))
