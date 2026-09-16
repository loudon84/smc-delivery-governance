# Composer

Composer inspects a business repository and installs only the resolved capability closure. It never authors Specs, plans or code.

Pipeline: analyze → resolve → source resolve → harness projection → reconcile. `.ges/project.yaml` `capabilities.requested` is the only later Desired State. Read-only commands write zero consumer bytes. Entry points are [[ges/cli/main.py#main]] and [[ges/compose.py#compose]].
