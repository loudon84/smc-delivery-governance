.PHONY: validate registry status next gate reconcile project-status program-status test

validate:
	python tools/validate_feature.py features/FEAT-SKILL-FIRST-001

registry:
	python tools/validate_registry.py

status:
	python tools/dependency_status.py features/FEAT-SKILL-FIRST-001

next:
	python tools/program_next.py programs/agent-platform/roadmap.yaml

gate:
	python tools/integration_gate.py features/FEAT-SKILL-FIRST-001

reconcile:
	python tools/reconcile_states.py features/FEAT-SKILL-FIRST-001
	python tools/reconcile_project_status.py

project-status:
	python tools/project_status.py

program-status:
	python tools/program_status.py agent-platform

test:
	pytest -q
