from __future__ import annotations

import os
import sys
from argparse import Namespace
from pathlib import Path

from ges.acceptance.golden_worktree import (
    DEFAULT_GOLDEN_SOURCE,
    create_detached_worktree,
    remove_worktree,
    resolve_consumer_head,
    source_dirty_status,
)
from ges.cli.capability import run_list
from ges.errors import GesError
from ges.reconciler.apply import consumer_tree


def main(argv: list[str] | None = None) -> int:
    del argv
    source = Path(os.environ.get("GES_ALPHA4_GOLDEN_REPO", str(DEFAULT_GOLDEN_SOURCE)))
    if not source.is_dir():
        print("GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED")
        return 3
    dirty, _, _ = source_dirty_status(source)
    if dirty:
        print("GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED")
        return 3
    worktree = None
    try:
        head = resolve_consumer_head(source)
        worktree = create_detached_worktree(source, head)
        before = consumer_tree(worktree)
        code = run_list(Namespace(repo=str(worktree), json=True))
        after = consumer_tree(worktree)
        if code != 0 or after != before:
            print("GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED")
            return 3
        print("GOLDEN_CAPABILITY_GOVERNANCE_OBSERVED")
        return 0
    except GesError as exc:
        print("GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED")
        print(f"{exc.code}: {exc.message}")
        return 3
    except Exception:
        print("GOLDEN_CAPABILITY_GOVERNANCE_BLOCKED")
        return 3
    finally:
        if worktree is not None:
            remove_worktree(source, worktree)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
