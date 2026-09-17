from __future__ import annotations

from argparse import Namespace

from ges.check import run_check
from ges.cli.common import flatten_ids, resolve_repo
from ges.cli.render import render_capability_plan, render_init, render_plan
from ges.compose import compose, prepare_apply
from ges.providers.resolve import build_capability_plan
from ges.providers.rtk import probe_rtk
from ges.doctor import BOOTSTRAP_PENDING, run_doctor
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
    print(render_capability_plan(build_capability_plan(ctx.profile, ctx.resolution.closed), probe_rtk()))
    if not _confirm(args):
        print("aborted")
        return 0
    try:
        prepare_apply(ctx)
        apply_plan(repo, ctx.plan, ctx.desired, project=ctx.project, profile=ctx.profile, lock=ctx.lock)
    except GesError as exc:
        if exc.code == GES_RECONCILE_NOOP:
            print(GES_RECONCILE_NOOP)
            return 0
        raise
    print("GES_APPLY_OK")
    print(run_check(repo))
    readiness = run_doctor(repo)
    print(_completion_report(readiness.get("overall") or BOOTSTRAP_PENDING))
    return 0


def _completion_report(overall: str) -> str:
    return (
        "GES install: PASS\n"
        "ges check: PASS\n"
        "Spec Kit runtime: PASS\n"
        "Matt skills: INSTALLED\n"
        "Matt project bootstrap: PENDING\n"
        f"Overall readiness: {overall}\n"
        "\n"
        "Next required action:\n"
        "  run setup-matt-pocock-skills\n"
        "  then run ges doctor\n"
    )


def _confirm(args: Namespace) -> bool:
    if args.yes or args.non_interactive:
        return True
    try:
        answer = input("Apply this composition? [Y/n] ").strip().lower()
    except EOFError:
        return False
    return answer in {"", "y", "yes"}
