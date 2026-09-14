"""Single contract-to-validator resolver shared by Delivery runtime gates."""
from __future__ import annotations
from pathlib import Path
CURRENT_PLAN_CONTRACT='smc.plan.v4.0'
VALIDATORS={
 'smc.plan.v3.3':'validate_plan_v33.py',
 'smc.plan.v3.4':'validate_plan_v34.py',
 'smc.plan.v3.5':'validate_plan_v35.py',
 'smc.plan.v3.6':'validate_plan_v36.py',
 'smc.plan.v3.7':'validate_plan_v37.py',
 'smc.plan.v4.0':'validate_plan_v40.py',
}
MODERN_METHOD_CONTRACTS=frozenset({'smc.plan.v3.7','smc.plan.v4.0'})
def validator_name(contract):return VALIDATORS.get(contract)
def validator_path(root:Path,contract:str):
 n=validator_name(contract);return root/'.agents/skills/smc-plan-validator/scripts'/n if n else None
def is_current_execution_contract(contract:str)->bool:
 return contract==CURRENT_PLAN_CONTRACT
