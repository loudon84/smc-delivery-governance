# Apply GES 5.0.0

The repository upgrade bundle is locked to commit 9f2c324793824ef46ee96b88bcd9175e70649004. Use bundle `verify.py`, then `upgrade.py <repository> --check`, then `upgrade.py <repository> --apply`. The last command validates before reporting PASS and automatically restores touched files after a failure. It never commits.

Consumer installation is separate: `python install.py <project>` is read-only; `--apply` uses a transaction backup under `.smc/skill-upgrade-backups/`. Use `rollback.py <project> --apply` for consumer rollback. Repository rollback instead uses the bundle `upgrade.py <repository> --rollback <printed-backup-directory>` and rejects post-upgrade edits.
