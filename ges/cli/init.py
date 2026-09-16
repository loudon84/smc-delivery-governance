from __future__ import annotations

from argparse import Namespace

from ges.check import run_check
from ges.cli.common import flatten_ids, resolve_repo
from ges.cli.render import render_init, render_plan
from ges.compose import compose, prepare_apply
from ges.errors import GES_RECONCILE_NOOP, GesError
from ges.legacy.v5 import inspect_legacy
from ges.reconciler.apply import apply_plan


def run(args: Namespace) -> int:
    repo = resolve_repo(args.repo)
    ctx = compose(
        repo,
        exclude=flatten_ids(args.exclude),
        extra=flatten_ids(getattr(args, "enable", None)),
        persist_profile=False,
    )
    legacy = inspect_legacy(repo)
    print(render_init(ctx, legacy))
    print(render_plan(ctx.plan.to_dict()))
    if not _confirm(args):
        print("aborted")
        return 0
    try:
        prepare_apply(ctx)
        apply_plan(repo, ctx.plan, ctx.desired, project=ctx.project, profile=ctx.profile, lock=ctx.lock)
    except GesError as exc:
        if exc.code == GES_RECONCILE_NOOP:
            print(GES_RECONCILE_NOOP)
        else:
            raise
    else:
        print("GES_APPLY_OK")
    print(run_check(repo))
    return 0


def _confirm(args: Namespace) -> bool:
    if args.yes or args.non_interactive:
        return True
    try:
        answer = input("Apply this composition? [Y/n] ").strip().lower()
    except EOFError:
        return False
    return answer in {"", "y", "yes"}
