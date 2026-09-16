# Reconcile

Installation is desired-versus-current reconciliation. Apply stages outside the consumer, snapshots T0, then commits receipt in the same transaction.

Unknown pre-existing files cannot be first-install UPDATEd. Apply runs `ges check` before success and keeps the T0 backup if rollback itself fails. Check is [[ges/check.py#run_check]].
