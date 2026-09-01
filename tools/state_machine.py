from __future__ import annotations
from pathlib import Path
from governance_lib import ROOT, load_yaml, dump_yaml, load_feature, load_work_packages, contract_catalog, repository_catalog


def transitions(kind:str)->dict[str,list[str]]:
    doc=load_yaml(ROOT/'contracts/lifecycle/states.yaml')
    return doc[kind]['transitions']


def allowed(kind:str,current:str,target:str)->bool:
    return target in transitions(kind).get(current,[])


def work_package_gate(feature_dir:Path, wp:dict, target:str)->list[str]:
    errors=[]
    ledger=feature_dir/'delivery-ledger'/f"{wp['repository_id']}.yaml"
    observed=load_yaml(ledger) if ledger.exists() else {}
    if target in {'PLANNED','IMPLEMENTING','REVIEW','VERIFIED','DONE'}:
        if wp.get('sync_state') not in {'SYNCED'}:
            errors.append(f"sync_state must be SYNCED, current={wp.get('sync_state')}")
    delivery=observed.get('delivery') or {}
    if target in {'PLANNED','IMPLEMENTING','REVIEW','VERIFIED','DONE'}:
        if not delivery.get('stage_prds'): errors.append('Stage PRD reference required')
        if not delivery.get('plans'): errors.append('Plan reference required')
    if target in {'REVIEW','VERIFIED','DONE'}:
        if not delivery.get('commits'): errors.append('implementation commit required')
    if target in {'VERIFIED','DONE'}:
        if (observed.get('acceptance') or {}).get('status') != 'PASS': errors.append('Acceptance PASS required')
    return errors


def feature_gate(feature_dir:Path, feature:dict, target:str)->list[str]:
    errors=[]
    wps=load_work_packages(feature_dir)
    if target in {'INTEGRATING','VERIFYING','DONE'}:
        not_ready=[wid for wid,wp in wps.items() if wp.get('status') not in {'VERIFIED','DONE'}]
        if not_ready: errors.append(f"work packages not VERIFIED/DONE: {not_ready}")
    if target=='DONE':
        scenario_id=(feature.get('integration') or {}).get('scenario_id')
        if scenario_id:
            scenario=load_yaml(ROOT/'integration/scenarios'/f"{feature['feature_id']}.yaml")
            if scenario.get('state')!='PASS': errors.append(f"integration {scenario_id} not PASS")
    return errors


def contract_gate(contract:dict,target:str)->list[str]:
    errors=[]; rel=contract.get('current_release') or {}
    if target in {'RELEASED','CONSUMED','CONFORMANCE_PASS'}:
        if not rel.get('version'): errors.append('release version required')
        if not rel.get('tag'): errors.append('release tag required')
        if not rel.get('peeled_commit'): errors.append('peeled commit required')
    return errors
