"""Deterministic risk routing from explicit, reviewable work facts."""
import argparse
import json
from pathlib import Path

REQUIRED = ('existing_owner', 'existing_capability', 'bounded_writes', 'deterministic_verification')
RISKS = ('new_owner', 'public_contract', 'security_boundary', 'schema_migration',
         'protocol_change', 'external_dependency', 'lifecycle_change',
         'cross_domain_ownership', 'live_acceptance')

def route(facts, previous=None):
    if not isinstance(facts, dict):
        raise ValueError('WORK_FACTS_INVALID')
    if previous is not None and previous not in {'NONE', 'LEAN', 'FULL'}:
        raise ValueError('PREVIOUS_PROFILE_INVALID')
    known = all(facts.get(k) is True for k in REQUIRED)
    safe = all(facts.get(k) is False for k in RISKS)
    reasons = [k for k in RISKS if facts.get(k) is not False]
    reasons += [k for k in REQUIRED if facts.get(k) is not True]
    if facts.get('research_only') is True and previous in {None, 'NONE'}:
        work, profile = 'SPIKE', 'NONE'
    elif known and safe and previous != 'FULL':
        work, profile = 'BOUNDED', ('LEAN' if facts.get('governed') is True or previous == 'LEAN' else 'NONE')
    else:
        work, profile = 'ARCHITECTURAL', 'FULL'
    return {'schema': 'smc.ges.work-route.v1', 'work_class': work,
            'governance_profile': profile, 'reasons': reasons, 'facts': facts}

def main():
    p=argparse.ArgumentParser();p.add_argument('facts',type=Path);p.add_argument('--previous-profile',choices=('NONE','LEAN','FULL'))
    a=p.parse_args();print(json.dumps(route(json.loads(a.facts.read_text(encoding='utf-8')),a.previous_profile),indent=2))
if __name__=='__main__': main()
