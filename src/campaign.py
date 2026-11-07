from pathlib import Path
import numpy as np,pandas as pd,json
def simulate(data_dir="data/generated",seed=20261022):
  p=Path(data_dir); rng=np.random.default_rng(seed); d=pd.read_csv(p/"ScoredCustomers.csv")
  price=d.plan_name.map({"Basic":19.,"Standard":39.,"Premium":69.})
  d["estimated_monthly_margin"]=price*.40
  d["eligible"]=(d.churn_probability>=.35)&(d.estimated_monthly_margin>=0)
  d["eligibility_reason"]=np.where(d.eligible,"risk threshold and positive margin","below risk threshold")
  d["group"]="not_contacted"; ix=np.flatnonzero(d.eligible.to_numpy())
  d.loc[ix,"group"]=np.where(rng.random(len(ix))<.5,"treatment","control")
  d["offer_id"]=np.where(d.group=="treatment","OFF-2026-000001",None)
  d["offer_cost"]=np.where(d.group=="treatment",np.minimum(price*.10*3,8.),0.)
  baseline=1-d.churn_probability.to_numpy()
  retain_p=np.where(d.group.to_numpy()=="treatment",np.minimum(1,baseline+.12),baseline)
  d["retained_6m"]=(rng.random(len(d))<retain_p).astype(int)
  d["campaign_contact_id"]=[f"CONTACT-{i:07d}" for i in range(1,len(d)+1)]
  d["contact_date"]="2026-01-01"; d["outcome_date"]="2026-07-01"
  d["retention_revenue"]=d.retained_6m*price*3
  d["net_value"]=d.retention_revenue-d.offer_cost
  d.to_csv(p/"CampaignContact.csv",index=False)
  d[["customer_id","retained_6m","retention_revenue","offer_cost","net_value"]].to_csv(p/"RetentionOutcome.csv",index=False)
  gt=json.loads((p/"ground_truth.json").read_text())
  pd.DataFrame(gt["anomalies"]).to_csv(p/"ExceptionRegister.csv",index=False)
  return d
def metrics(d):
  e=d[d.eligible]; t=e[e.group=="treatment"]; c=e[e.group=="control"]
  tr=float(t.retained_6m.mean()) if len(t) else 0.; cr=float(c.retained_6m.mean()) if len(c) else 0.
  lift=tr-cr; cost=float(t.offer_cost.sum()); incr=max(0,lift)*len(t)
  avg=float(t.plan_name.map({"Basic":19.,"Standard":39.,"Premium":69.}).mean()) if len(t) else 0.
  value=incr*avg*3; return {"eligible":len(e),"treatment_n":len(t),"control_n":len(c),
    "treatment_retention":tr,"control_retention":cr,"incremental_lift":lift,"campaign_cost":cost,
    "estimated_incremental_retained":incr,"estimated_roi":(value-cost)/cost if cost else 0.}
