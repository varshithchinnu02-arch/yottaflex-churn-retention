from pathlib import Path
import joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score,precision_score,recall_score,accuracy_score
FEATURES=["plan_name","tenure_months","avg_usage_3m","usage_trend","late_payment_rate","support_cases_6m","overdue_balance","seasonal"]
NUM=FEATURES[1:]
def train(data_dir="data/generated",model_dir="models"):
  p=Path(data_dir); df=pd.read_csv(p/"PredictionFeatures.csv"); X=df[FEATURES]; y=df.churn_label
  if y.nunique()<2: raise ValueError("Need both churn and non-churn labels; increase customer count.")
  a,b,c,d=train_test_split(X,y,test_size=.25,random_state=20261022,stratify=y)
  prep=ColumnTransformer([("num",Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),NUM),
    ("cat",OneHotEncoder(handle_unknown="ignore"),["plan_name"])])
  model=Pipeline([("prep",prep),("clf",LogisticRegression(max_iter=500,class_weight="balanced"))])
  model.fit(a,c); prob=model.predict_proba(b)[:,1]; pred=(prob>=.5).astype(int)
  metrics={"roc_auc":float(roc_auc_score(d,prob)),"precision":float(precision_score(d,pred,zero_division=0)),
    "recall":float(recall_score(d,pred,zero_division=0)),"accuracy":float(accuracy_score(d,pred)),"test_rows":len(d)}
  Path(model_dir).mkdir(parents=True,exist_ok=True); joblib.dump(model,Path(model_dir)/"churn_model.joblib")
  scored=df.copy(); scored["churn_probability"]=model.predict_proba(X)[:,1]
  scored["risk_band"]=pd.cut(scored.churn_probability,[-.001,.35,.65,1],labels=["Low","Medium","High"]).astype(str)
  scored.to_csv(p/"ScoredCustomers.csv",index=False)
  return metrics
if __name__=="__main__": print(train())
