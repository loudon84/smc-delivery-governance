# Doctor

`ges doctor` observes runtime readiness without writing the consumer. Preflight does not require `.ges` state.

`--preflight` checks Python, git and Cursor. `spec_kit_runtime` is official projection identity, not stub script execution. Doctor is not Spec Kit Functional Ready. Implementation is [[ges/doctor.py#run_doctor]] and [[ges/doctor.py#run_preflight]].

Alpha.3 adds ephemeral `capabilities[]` and `warnings[]` for RTK verify. Missing recommended RTK is WARNING and does not BLOCK overall. See [[capability-resolver]].
