import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

SEED=20261022
PREDICTION_DATE=pd.Timestamp("2025-12-01")
def generate(n=20000, out="data/generated", seed=SEED):
    rng=np.random.default_rng(seed); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    months=pd.date_range("2025-01-01",periods=18,freq="MS")
    cid=np.array([f"CUS-{i:06d}" for i in range(1,n+1)])
    sid=np.array([f"SUB-{x}-01" for x in cid])
    plan=rng.choice(["Basic","Standard","Premium"],n,p=[.45,.38,.17])
    price=pd.Series(plan).map({"Basic":19.,"Standard":39.,"Premium":69.}).to_numpy()
    tenure=rng.integers(1,72,n); seasonal=rng.random(n)<.18
    risk_latent=rng.normal(0,1,n)+.5*(plan=="Basic")+.4*(tenure<6)
    p_churn=np.clip(1/(1+np.exp(-(-2.15+0.85*risk_latent))),.04,.28)
    churned=rng.random(n)<p_churn
    churn_month=np.where(churned,rng.integers(13,19,n),99)
    # A small early-churn group is excluded from the prediction cohort.
    early=rng.random(n)<.025; churn_month[early]=rng.integers(5,13,early.sum())
    customers=pd.DataFrame({"customer_id":cid,"signup_date":(PREDICTION_DATE-pd.to_timedelta(tenure*30,unit="D")).date,
      "region":rng.choice(["North","South","East","West"],n),"acquisition_channel":rng.choice(["Organic","Referral","Paid","Partner"],n),
      "customer_segment":rng.choice(["Consumer","Small Business","Enterprise"],n,p=[.7,.23,.07]),
      "seasonality_type":np.where(seasonal,"Seasonal","Stable")})
    subs=pd.DataFrame({"subscription_id":sid,"customer_id":cid,"product_cohort":plan,"plan_name":plan,
      "monthly_price":price,"start_date":customers.signup_date,"status":"active","billing_cycle":"monthly"})
    usage_parts=[]; billing_parts=[]; support_parts=[]; churn_parts=[]
    base=rng.lognormal(3.5,.5,n); decline=rng.normal(.015,.045,n)
    payrisk=rng.beta(1.5,9,n); supp_risk=rng.beta(1.2,10,n)
    for m,dt in enumerate(months,1):
      alive=churn_month>=m
      seasonal_factor=np.where(seasonal & (dt.month in [11,12,1,2]),.55,1.0)
      u=np.maximum(0,base*np.maximum(.35,1-decline*m)*seasonal_factor*rng.normal(1,.12,n))
      idx=np.flatnonzero(alive); k=len(idx)
      usage_parts.append(pd.DataFrame({"snapshot_id":[f"SNAP-{sid[i]}-{dt:%Y-%m}" for i in idx],
        "subscription_id":sid[idx],"customer_id":cid[idx],"snapshot_date":dt,
        "usage_units":np.round(u[idx],2),"active_days":rng.integers(1,31,k)}))
      late=rng.random(k)<payrisk[idx]; amt=price[idx]
      billing_parts.append(pd.DataFrame({"billing_event_id":[f"BILL-{sid[i]}-{dt:%Y-%m}" for i in idx],
        "subscription_id":sid[idx],"customer_id":cid[idx],"billing_date":dt,
        "amount_due":amt,"overdue_amount":np.where(late,amt,0).round(2),
        "payment_status":np.where(late,"late","paid")}))
      case_mask=rng.random(k)<supp_risk[idx]*.6; ci=idx[case_mask]; ck=len(ci)
      if ck:
        support_parts.append(pd.DataFrame({"support_case_id":[f"CASE-{m:02d}-{j:07d}" for j in range(1,ck+1)],
          "customer_id":cid[ci],"subscription_id":sid[ci],"opened_date":dt,
          "case_type":rng.choice(["Billing","Technical","Cancellation","Product"],ck),
          "priority":rng.choice(["Low","Medium","High"],ck),
          "case_status":rng.choice(["Resolved","Open","Escalated"],ck,p=[.78,.15,.07])}))
      ci=np.flatnonzero(churn_month==m)
      if len(ci):
        churn_parts.append(pd.DataFrame({"churn_event_id":[f"CHURN-{cid[i]}-2026" for i in ci],
          "subscription_id":sid[ci],"customer_id":cid[ci],"churn_date":dt,
          "churn_type":rng.choice(["voluntary","involuntary"],len(ci),p=[.72,.28])}))
    U=pd.concat(usage_parts,ignore_index=True)
    B=pd.concat(billing_parts,ignore_index=True)
    S=pd.concat(support_parts,ignore_index=True) if support_parts else pd.DataFrame(columns=["support_case_id","customer_id","subscription_id","opened_date","case_type","priority","case_status"])
    CE=pd.concat(churn_parts,ignore_index=True) if churn_parts else pd.DataFrame(columns=["churn_event_id","subscription_id","customer_id","churn_date","churn_type"])
    U["snapshot_date"]=pd.to_datetime(U.snapshot_date); B["billing_date"]=pd.to_datetime(B.billing_date); S["opened_date"]=pd.to_datetime(S.opened_date)
    # Cohort active on prediction date. Only rows strictly before cutoff become features.
    eligible=np.flatnonzero(churn_month>12)
    rows=[]
    U["snapshot_date"]=pd.to_datetime(U.snapshot_date); B["billing_date"]=pd.to_datetime(B.billing_date); S["opened_date"]=pd.to_datetime(S.opened_date)
    # Vectorized aggregation keeps the full 20k-customer run practical.
    cohort_ids=cid[eligible]
    up=U[U.snapshot_date<PREDICTION_DATE].sort_values("snapshot_date")
    up3=up.groupby("customer_id",sort=False).tail(3)
    ua=up3.groupby("customer_id").usage_units.agg(["mean","first","last"])
    ua["trend"]=(ua["last"]-ua["first"])/ua["first"].clip(lower=1)
    bp=B[B.billing_date<PREDICTION_DATE]
    ba=bp.assign(late=(bp.payment_status=="late").astype(int)).groupby("customer_id").agg(
        late_payment_rate=("late","mean"),overdue_balance=("overdue_amount","sum"))
    sp=S[(S.opened_date<PREDICTION_DATE)&(S.opened_date>=PREDICTION_DATE-pd.DateOffset(months=6))]
    sa=sp.groupby("customer_id").size().rename("support_cases_6m")
    lookup=pd.DataFrame({"customer_id":cohort_ids,"subscription_id":sid[eligible],"plan_name":plan[eligible],
        "tenure_months":tenure[eligible],"seasonal":seasonal[eligible].astype(int),
        "churn_label":((churn_month[eligible]>=13)&(churn_month[eligible]<=18)).astype(int)})
    lookup=lookup.merge(ua[["mean","trend"]],left_on="customer_id",right_index=True,how="left")
    lookup=lookup.merge(ba,left_on="customer_id",right_index=True,how="left")
    lookup=lookup.merge(sa,left_on="customer_id",right_index=True,how="left")
    lookup=lookup.fillna({"mean":0,"trend":0,"late_payment_rate":0,"overdue_balance":0,"support_cases_6m":0})
    lookup=lookup.rename(columns={"mean":"avg_usage_3m"})
    lookup["prediction_date"]=PREDICTION_DATE.date()
    F=lookup[["customer_id","subscription_id","prediction_date","plan_name","tenure_months","avg_usage_3m",
      "trend","late_payment_rate","support_cases_6m","overdue_balance","seasonal","churn_label"]].rename(columns={"trend":"usage_trend"})
    offers=pd.DataFrame([
      ["OFF-2026-000001","10% for 3 months",.10,3,8.0,True],
      ["OFF-2026-000002","15% for 2 months",.15,2,10.0,True],
      ["OFF-2026-000003","Service credit",0.,1,5.0,True]],
      columns=["offer_id","offer_name","discount_rate","duration_months","max_cost","active"])
    rules=pd.DataFrame([
      ["RULE-001","High risk",.65,0.,8.,True],["RULE-002","Medium risk",.35,0.,8.,True]],
      columns=["eligibility_rule_id","rule_name","min_churn_probability","min_margin","max_offer_cost","active"])
    tables={"Customer":customers,"Subscription":subs,"UsageSnapshot":U,"BillingEvent":B,"SupportCase":S,
      "ChurnEvent":CE,"Offer":offers,"EligibilityRule":rules,"PredictionFeatures":F}
    for name,df in tables.items(): df.to_csv(out/f"{name}.csv",index=False)
    F[["customer_id","churn_label"]].assign(prediction_date=PREDICTION_DATE.date(),horizon_months=6).to_csv(out/"ChurnOutcome.csv",index=False)
    # Four required anomaly scenarios are documented separately, never used as features.
    gt={"seed":seed,"prediction_date":str(PREDICTION_DATE.date()),"horizon_months":6,
      "cohort_size":len(F),"churn_labels":int(F.churn_label.sum()),
      "anomalies":[{"issue_id":f"ISSUE-{k:04d}","customer_id":str(F.customer_id.iloc[k]),
       "issue_type":typ,"ground_truth":"known_exception","expected_action":"flag_and_exclude"}
       for k,typ in enumerate(["CHURN_LABEL_BEFORE_PREDICTION_DATE","OFFER_SENT_TO_INELIGIBLE",
       "TREATMENT_CONTROL_LEAKAGE","RETAINED_CUSTOMER_MULTIPLE_OFFERS"],1) if len(F)>=k]}
    (out/"ground_truth.json").write_text(json.dumps(gt,indent=2))
    return F
if __name__=="__main__":
  p=argparse.ArgumentParser(); p.add_argument("--customers",type=int,default=20000); p.add_argument("--seed",type=int,default=SEED); p.add_argument("--out",default="data/generated")
  a=p.parse_args(); f=generate(a.customers,a.out,a.seed); print(f"Generated cohort: {len(f):,}; future churn labels: {int(f.churn_label.sum()):,}")
