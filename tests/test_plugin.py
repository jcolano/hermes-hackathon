import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('growth_plugin',ROOT/'__init__.py',submodule_search_locations=[str(ROOT)])
pkg=importlib.util.module_from_spec(spec)
sys.modules['growth_plugin']=pkg
spec.loader.exec_module(pkg)
from growth_plugin import tools

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        os.environ['HERMES_HOME']=self.tmp.name
    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop('HERMES_HOME',None)
    def call(self,fn,**args):
        return json.loads(getattr(tools,fn)(args))
    def test_demo_and_plan(self):
        b=self.call('growth_list_businesses')['businesses']
        self.assertEqual(len(b),2)
        self.assertTrue(self.call('growth_diagnose',business_id=b[0]['business_id'])['ok'])
        self.assertEqual(self.call('growth_plan',business_id=b[0]['business_id'])['plan']['duration_days'],30)
    def test_approval_gate_and_persistence(self):
        a=self.call('growth_propose_action',business_id='miami-alterations-demo',opportunity_id='retention')['action']
        aid=a['action_id']
        self.assertFalse(self.call('growth_execute_action',action_id=aid)['ok'])
        self.assertFalse(self.call('growth_approve_action',action_id=aid,approval_code='BAD',owner_confirmation=True)['ok'])
        self.assertFalse(self.call('growth_approve_action',action_id=aid,approval_code=a['approval_code'],owner_confirmation=False)['ok'])
        self.assertTrue(self.call('growth_approve_action',action_id=aid,approval_code=a['approval_code'],owner_confirmation=True)['ok'])
        self.assertTrue(self.call('growth_execute_action',action_id=aid)['action']['result']['simulated'])
        self.assertEqual(self.call('growth_action_status',action_id=aid)['action']['status'],'simulated')
        self.assertFalse(self.call('growth_execute_action',action_id=aid)['ok'])
    def test_missing_data(self):
        x=self.call('growth_upsert_business',business_id='new-shop',name='New Shop',industry='retail',location='Miami')
        self.assertTrue(x['ok'])
        self.assertEqual(self.call('growth_opportunities',business_id='new-shop')['opportunities'],[])
        self.assertEqual(self.call('growth_diagnose',business_id='new-shop')['diagnosis']['data_completeness'],0)
    def test_registration(self):
        class Ctx:
            def __init__(self):self.names=[]
            def register_tool(self,**kw):self.names.append(kw['name'])
        ctx=Ctx();pkg.register(ctx)
        self.assertEqual(len(ctx.names),9)
        self.assertEqual(set(ctx.names),set(pkg.schemas.SCHEMAS))

if __name__=='__main__':unittest.main()
