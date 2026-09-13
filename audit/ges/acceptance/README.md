# Pilot evidence layout

Place dynamic pilot evidence under:

```text
audit/ges/acceptance/<candidate>/pilots/<delivery-id>/
```

Each delivery directory must contain the files listed in `verify_pilot_evidence.py`.

Do not store full prompts, source, or secrets.

```bash
python engineeing-skills/acceptance/verify_pilot_evidence.py audit/ges/acceptance/<candidate>/pilots
```

Missing evidence returns `PILOT_EVIDENCE_INCOMPLETE`.
