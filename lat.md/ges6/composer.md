# Composer

Composer inspects a business repository and installs only the resolved capability closure. It never authors Specs, plans or code.

Pipeline: analyze → resolve → source resolve → harness projection → reconcile. After first install the requested set is frozen. `ges doctor` observes readiness. Entry points are [[ges/cli/main.py#main]], [[ges/compose.py#compose]] and [[ges/doctor.py#run_doctor]].
