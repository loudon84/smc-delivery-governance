.PHONY: validate status next gate test
validate:
	python tools/validate_feature.py features/FEAT-SKILL-FIRST-001
status:
	python tools/dependency_status.py features/FEAT-SKILL-FIRST-001
next:
	python tools/program_next.py programs/agent-platform/roadmap.yaml
gate:
	python tools/integration_gate.py features/FEAT-SKILL-FIRST-001
test:
	pytest -q
