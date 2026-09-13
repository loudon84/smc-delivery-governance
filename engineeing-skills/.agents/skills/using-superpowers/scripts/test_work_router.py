import unittest
from work_router import route, REQUIRED, RISKS
class RoutingTests(unittest.TestCase):
    def facts(self): return {**dict.fromkeys(REQUIRED,True),**dict.fromkeys(RISKS,False),'governed':True}
    def test_governed_lean(self): self.assertEqual(route(self.facts())['governance_profile'],'LEAN')
    def test_unknown_forces_full(self): self.assertEqual(route({})['governance_profile'],'FULL')
    def test_no_downgrade(self): self.assertEqual(route(self.facts(),'FULL')['governance_profile'],'FULL')
    def test_each_risk(self):
        for risk in RISKS:
            f=self.facts();f[risk]=True;self.assertEqual(route(f)['governance_profile'],'FULL')
if __name__=='__main__': unittest.main()
