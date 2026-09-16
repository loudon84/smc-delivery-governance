# Doctor

`ges doctor` observes runtime readiness without writing the consumer. Preflight does not require `.ges` state.

`--preflight` checks Python, git and Cursor. Full doctor separates materialized `ges check` from Matt bootstrap PENDING vs READY. Implementation is [[ges/doctor.py#run_doctor]] and [[ges/doctor.py#run_preflight]].
