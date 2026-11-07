from src.generate import generate
from src.model import train
from src.campaign import simulate,metrics
from src.validate import validate
def test_pipeline(tmp_path):
 p=tmp_path/"data"; generate(700,p,20261022)
 assert validate(p)["passed"]
 m=train(p,tmp_path/"models"); assert 0<=m["roc_auc"]<=1
 d=simulate(p,20261022); cm=metrics(d)
 assert cm["treatment_n"]+cm["control_n"]==cm["eligible"]
 assert d.customer_id.is_unique
