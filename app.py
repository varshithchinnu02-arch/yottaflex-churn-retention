from pathlib import Path
import streamlit as st,pandas as pd,plotly.express as px
from src.generate import generate
from src.model import train
from src.campaign import simulate,metrics
from src.validate import validate
st.set_page_config(page_title="YottaFlex Churn Lab",layout="wide")
st.title("YottaFlex | Churn & Retention Intelligence")
st.caption("Synthetic-data prototype • Seed 20261022 • Prediction date 2025-12-01 • Six-month horizon")
p=Path("data/generated")
st.sidebar.header("Pipeline controls")
if st.sidebar.button("1. Generate 2,000-customer demo"):
 generate(2000); st.sidebar.success("Data generated"); st.rerun()
if st.sidebar.button("2. Train / score model"):
 m=train(); st.sidebar.write(m); st.rerun()
if st.sidebar.button("3. Simulate retention campaign"):
 simulate(); st.sidebar.success("Campaign complete"); st.rerun()
if not (p/"PredictionFeatures.csv").exists():
 st.info("Use sidebar to generate the demo dataset, or run the 20,000-customer CLI pipeline. See README.")
 st.stop()
tabs=st.tabs(["Overview","Customer risk","Campaign","Data quality"])
with tabs[0]:
 f=pd.read_csv(p/("ScoredCustomers.csv" if (p/"ScoredCustomers.csv").exists() else "PredictionFeatures.csv"))
 a,b,c,d=st.columns(4); a.metric("Prediction cohort",f"{len(f):,}"); b.metric("Future churn labels",f"{int(f.churn_label.sum()):,}")
 c.metric("Horizon churn rate",f"{f.churn_label.mean():.1%}"); d.metric("High-risk",f"{int((f.churn_probability>=.65).sum()):,}" if "churn_probability" in f else "Train model")
 if "churn_probability" in f: st.plotly_chart(px.histogram(f,x="churn_probability",color="risk_band",title="Churn risk score distribution"),use_container_width=True)
 st.info("Feature window ends before 2025-12-01. Labels represent churn from 2026-01-01 through 2026-06-30.")
with tabs[1]:
 if (p/"ScoredCustomers.csv").exists():
  f=pd.read_csv(p/"ScoredCustomers.csv"); band=st.selectbox("Risk band",["All","Low","Medium","High"])
  if band!="All": f=f[f.risk_band==band]
  st.dataframe(f.sort_values("churn_probability",ascending=False).head(500),use_container_width=True)
 else: st.warning("Train model first.")
with tabs[2]:
 if (p/"CampaignContact.csv").exists():
  f=pd.read_csv(p/"CampaignContact.csv"); m=metrics(f)
  cols=st.columns(4); cols[0].metric("Eligible",m["eligible"]); cols[1].metric("Treatment",f'{m["treatment_retention"]:.1%}')
  cols[2].metric("Control",f'{m["control_retention"]:.1%}'); cols[3].metric("Incremental lift",f'{m["incremental_lift"]:+.1%}')
  st.write(f'Campaign cost: ${m["campaign_cost"]:,.2f} • Estimated ROI: {m["estimated_roi"]:.2f}x')
  st.plotly_chart(px.histogram(f[f.group.isin(["treatment","control"])],x="group",color="retained_6m",barmode="group"),use_container_width=True)
 else: st.warning("Run campaign simulation first.")
with tabs[3]:
 r=validate(); st.metric("Validation", "PASS" if r["passed"] else "FAIL")
 st.json(r)
 if (p/"ExceptionRegister.csv").exists(): st.dataframe(pd.read_csv(p/"ExceptionRegister.csv"))
