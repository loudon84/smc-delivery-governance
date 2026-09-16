from __future__ import annotations

import argparse
import sys

from ges import __version__
from ges.cli import analyze, apply, check, diff, init, legacy, remove
from ges.errors import GesError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ges", description="GES 6 Composer")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="analyze, resolve, confirm, apply, check")
    _repo(init_p)
    _select(init_p)
    init_p.set_defaults(func=init.run)

    analyze_p = sub.add_parser("analyze", help="deterministic repo profile")
    _repo(analyze_p)
    analyze_p.set_defaults(func=analyze.run)

    diff_p = sub.add_parser("diff", help="show desired vs current plan")
    _repo(diff_p)
    _select(diff_p)
    diff_p.add_argument("--json", action="store_true")
    diff_p.set_defaults(func=diff.run)

    apply_p = sub.add_parser("apply", help="reconcile desired state")
    _repo(apply_p)
    _select(apply_p)
    apply_p.set_defaults(func=apply.run)

    check_p = sub.add_parser("check", help="validate composed project state")
    _repo(check_p)
    check_p.set_defaults(func=check.run)

    remove_p = sub.add_parser("remove", help="remove GES-owned projection")
    _repo(remove_p)
    remove_p.set_defaults(func=remove.run)

    legacy_p = sub.add_parser("legacy", help="inspect or remove GES v5 leftovers")
    legacy_sub = legacy_p.add_subparsers(dest="legacy_command", required=True)
    inspect_p = legacy_sub.add_parser("inspect")
    _repo(inspect_p)
    inspect_p.set_defaults(func=legacy.run_inspect)
    lremove = legacy_sub.add_parser("remove")
    _repo(lremove)
    lremove.add_argument("--dry-run", action="store_true", default=True)
    lremove.add_argument("--apply", action="store_true")
    lremove.add_argument("--force", action="store_true")
    lremove.set_defaults(func=legacy.run_remove)
    return parser


def _repo(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("repo", nargs="?", default=".")


def _select(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exclude", action="append", default=[], dest="exclude")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GesError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        if exc.code == "GES_RECONCILE_NOOP":
            print(exc.code)
            return 0
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
