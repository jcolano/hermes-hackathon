import json,os,secrets,threading
from pathlib import Path
from . import engine
LOCK=threading.RLock()
def statefile():
 p=Path(os.environ.get("HERMES_HOME",str(Path.home()/".hermes")))/"plugin-data"/"smb-growth-agent"/"state.json";p.parent.mkdir(parents=True,exist_ok=True);return p
def load():
 p=statefile()
 return json.loads(p.read_text()) if p.exists() else {"businesses":{x["business_id"]:x for x in json.loads((Path(__file__).parent/"data"/"demo_businesses.json").read_text())},"actions":{}}
def save(s):
 p=statefile();t=p.with_suffix(".tmp");t.write_text(json.dumps(s));os.replace(t,p)
def run(f):
 try:
  with LOCK:return json.dumps({"ok":True,**f()})
 except Exception as e:return json.dumps({"ok":False,"error":str(e)})
def business(s,a):return s["businesses"][a["business_id"]]
def growth_list_businesses(args):return run(lambda:{"businesses":list(load()["businesses"].values())})
def growth_upsert_business(args):
 def f():
  s=load();b={**args,"demo":False};b.setdefault("metrics",{});s["businesses"][args["business_id"]]=b;save(s);return {"business":b}
 return run(f)
def growth_diagnose(args):return run(lambda:{"diagnosis":engine.diagnosis(business(load(),args))})
def growth_opportunities(args):return run(lambda:{"opportunities":engine.opportunities(business(load(),args))})
def growth_plan(args):return run(lambda:{"plan":engine.plan(business(load(),args))})
def growth_propose_action(args):
 def f():
  s=load();b=business(s,args);o=next(x for x in engine.opportunities(b) if x["id"]==args["opportunity_id"]);i="act_"+secrets.token_hex(8);a={"action_id":i,"business_id":b["business_id"],"opportunity_id":o["id"],"title":o["title"],"proposed_steps":o["recommended_action"],"status":"proposed","approval_code":secrets.token_hex(4).upper(),"mode":"simulation_only"};s["actions"][i]=a;save(s);return {"action":a}
 return run(f)
def growth_approve_action(args):
 def f():
  s=load();a=s["actions"][args["action_id"]]
  if a["status"]!="proposed" or args.get("owner_confirmation") is not True or not secrets.compare_digest(a["approval_code"],args.get("approval_code","")):raise ValueError("Explicit approval and matching code required")
  a["status"]="approved";a.pop("approval_code");save(s);return {"action":a}
 return run(f)
def growth_execute_action(args):
 def f():
  s=load();a=s["actions"][args["action_id"]]
  if a["status"]!="approved":raise ValueError("Approval required")
  a["status"]="simulated";a["result"]={"simulated":True,"external_effects":False};save(s);return {"action":a}
 return run(f)
def growth_action_status(args):return run(lambda:{"action":load()["actions"][args["action_id"]]})
