from __future__ import annotations

import argparse
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import yaml

from artifact_verify import verify_receipt_semantics
from governance_lib import (
    EXIT_EXPECTED_NON_READY,
    EXIT_OK,
    EXIT_SYSTEM_ERROR,
    ROOT,
    contract_release,
    dump_yaml,
    github_api,
    github_file,
    load_feature,
    load_work_packages,
    repository_catalog,
    validate_jsonschema,
)

def discover_github(repo_name: str, wp_id: str, token=None):
    # Search is a convenience projection, never primary lifecycle evidence.
    q = f'repo:{repo_name} label:"gov:wp:{wp_id}"'
    data = github_api("/search/issues?q=" + urllib.parse.quote(q) + "&per_page=100", token=token)
    issues, bugs, prs = [], [], []
    for item in data.get("items", []):
        labels = [x["name"] for x in item.get("labels", [])]
        ref = {
            "number": item["number"],
            "state": item["state"],
            "title": item["title"],
            "url": item["html_url"],
            "labels": labels,
        }
        if item.get("pull_request"):
            # Search API does not reliably expose merged_at. Fetch PR detail.
            try:
                pr = github_api(f"/repos/{repo_name}/pulls/{item['number']}", token=token)
                ref["state"] = "merged" if pr.get("merged_at") else pr.get("state", item["state"])
            except RuntimeError:
                ref["state"] = item["state"]
            prs.append(ref)
        elif "gov:type:bug" in labels:
            bugs.append(ref)
        else:
            issues.append(ref)
    return issues, bugs, prs

def load_receipt_text(repo: dict, receipt_path: str, args) -> tuple[str | None, str | None]:
    if args.local_receipt_dir:
        local = Path(args.local_receipt_dir) / f"{repo['repository_id']}.yaml"
        if not local.exists():
            return None, None
        return local.read_text(encoding="utf-8"), str(local)
    try:
        text = github_file(repo["name"], receipt_path, repo["default_branch"], token=args.token)
        return text, receipt_path
    except RuntimeError as exc:
        message = str(exc)
        if "GitHub API 401" in message or "GitHub API 403" in message:
            raise SystemExit(EXIT_SYSTEM_ERROR) from exc
        raise

def provider_receipt_ok(receipt: dict, wp: dict) -> bool:
    if wp.get("role") != "provider" or not wp.get("contract_outputs"):
        return True
    evidence = receipt.get("evidence") or {}
    release = evidence.get("release") or {}
    commits = receipt.get("delivery", {}).get("commits") or []
    return bool(release.get("tag") and release.get("commit") and commits)

def _refresh_traceability(fdir: Path, wps: dict) -> None:
    trace_path = fdir / "traceability.yaml"
    if not trace_path.exists():
        return
    trace = yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    by_id = {item["work_package_id"]: item for item in trace.get("work_packages", [])}
    for wid, wp in wps.items():
        ledger_path = fdir / "delivery-ledger" / f"{wp['repository_id']}.yaml"
        if not ledger_path.exists():
            continue
        ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
        delivery = ledger.get("delivery") or {}
        item = by_id.get(wid) or {"work_package_id": wid, "repository_id": wp["repository_id"]}
        for src,dst in [
            ("stage_prds","stage_prds"),("issues","issues"),("bugs","bugs"),
            ("plans","plans"),("commits","commits"),("verification_reports","verification"),
        ]:
            item[dst] = delivery.get(src) or []
        by_id[wid] = item
    trace["work_packages"] = list(by_id.values())
    dump_yaml(trace_path, trace)

# @lat: [[facts-and-evidence#Delivery Ledger]]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--discover-github",action="store_true")
    ap.add_argument("--token")
    ap.add_argument("--local-receipt-dir")
    ap.add_argument("--offline-semantic",action="store_true",
                    help="Skip GitHub semantic ArtifactRef verification; only for tests/dev")
    args=ap.parse_args()

    fdir,feature=load_feature(args.feature)
    wps=load_work_packages(fdir)
    repos=repository_catalog()
    expected_non_ready=False

    for wid,wp in wps.items():
        repo=repos.get(wp["repository_id"])
        if not repo:
            print(f"{wid}: DIVERGED unknown repository");expected_non_ready=True;continue
        receipt_path=f"{repo['governance']['delivery_receipts'].rstrip('/')}/{wid}.yaml"
        try:
            text,resolved_path=load_receipt_text(repo,receipt_path,args)
        except SystemExit: raise
        except Exception as exc:
            print(f"{wid}: SYSTEM_ERROR {exc}");raise SystemExit(EXIT_SYSTEM_ERROR) from exc

        if text is None:
            print(f"{wid}: MISSING_RECEIPT {receipt_path}")
            if args.apply:
                path=fdir/"work-packages"/Path(wp["_path"]).name
                clean={k:v for k,v in wp.items() if k!="_path"}
                clean["sync_state"]="MISSING_RECEIPT"
                clean.pop("delivery_receipt",None);clean.pop("observed",None)
                dump_yaml(path,clean)
            expected_non_ready=True;continue

        try: receipt=yaml.safe_load(text)
        except Exception as exc:
            print(f"{wid}: DIVERGED invalid yaml: {exc}");expected_non_ready=True;continue

        errors=validate_jsonschema(receipt,ROOT/"schemas/delivery-receipt.schema.json")
        if not errors and not args.offline_semantic and not args.local_receipt_dir:
            try:
                errors.extend(verify_receipt_semantics(receipt,token=args.token))
            except RuntimeError as exc:
                print(f"{wid}: SYSTEM_ERROR semantic verification: {exc}")
                raise SystemExit(EXIT_SYSTEM_ERROR) from exc
        if errors:
            print(f"{wid}: DIVERGED invalid receipt/evidence: {errors[0]}")
            if args.apply:
                path=fdir/"work-packages"/Path(wp["_path"]).name
                clean={k:v for k,v in wp.items() if k!="_path"};clean["sync_state"]="DIVERGED";dump_yaml(path,clean)
            expected_non_ready=True;continue

        if receipt["feature_id"]!=feature["feature_id"] or receipt["work_package_id"]!=wid or receipt["repository_id"]!=wp["repository_id"]:
            print(f"{wid}: DIVERGED identity mismatch");expected_non_ready=True;continue

        sync_state="SYNCED"
        if receipt["source_revision"]!=feature["source_revision"] or receipt["source_revision"]!=wp["source_revision"]:
            sync_state="STALE_FEATURE"

        expected={x["contract_id"]:x.get("version") or x.get("required_version") for x in wp.get("contract_inputs",[])}
        actual={x["contract_id"]:x for x in (receipt.get("sync") or {}).get("contract_pins",[])}
        for cid,ver in expected.items():
            pin=actual.get(cid) or {}
            rel=contract_release(cid,ver) if ver else None
            if ver and pin.get("version")!=ver:
                sync_state="STALE_CONTRACT"
            if ver and (not pin.get("tag") or not pin.get("commit")):
                sync_state="STALE_CONTRACT"
            if rel and (pin.get("tag")!=rel.get("tag") or pin.get("commit")!=rel.get("peeled_commit")):
                sync_state="STALE_CONTRACT"

        claimed=receipt["status"]
        if claimed in {"VERIFIED","DONE"} and wp.get("role")=="provider" and wp.get("contract_outputs"):
            if not provider_receipt_ok(receipt,wp): sync_state="DIVERGED"
        # Consumer PASS in the remote receipt is NOT trusted. Central verified attestation is authoritative.

        if args.discover_github and not args.local_receipt_dir:
            try:
                issues,bugs,prs=discover_github(repo["name"],wid,args.token)
                receipt["delivery"]["issues"]=issues;receipt["delivery"]["bugs"]=bugs;receipt["delivery"]["pull_requests"]=prs
            except RuntimeError as exc:
                msg=str(exc)
                if "GitHub API 401" in msg or "GitHub API 403" in msg:
                    print(f"{wid}: SYSTEM_ERROR GitHub auth failed");raise SystemExit(EXIT_SYSTEM_ERROR) from exc
                print(f"{wid}: GitHub discovery warning: {exc}")

        print(f"{wid}: {sync_state} local={claimed} central={wp['status']}")
        if args.apply:
            existing={}
            ledger_path=fdir/"delivery-ledger"/f"{wp['repository_id']}.yaml"
            if ledger_path.exists():
                existing=load_yaml(ledger_path) or {}
            ledger={
                "feature_id":feature["feature_id"],"work_package_id":wid,"repository_id":wp["repository_id"],
                "source_revision":receipt["source_revision"],"observed_at":datetime.now(timezone.utc).isoformat(),
                "receipt_path":resolved_path or receipt_path,"status":claimed,"sync_state":sync_state,
                "delivery":receipt["delivery"],
                "acceptance_claimed":receipt.get("acceptance"),
                "evidence":receipt.get("evidence",{}),
            }
            if existing.get("acceptance_verified"):
                ledger["acceptance_verified"]=existing["acceptance_verified"]
            dump_yaml(ledger_path,ledger)

            path=fdir/"work-packages"/Path(wp["_path"]).name
            clean={k:v for k,v in wp.items() if k!="_path"}
            clean["sync_state"]=sync_state
            clean["delivery_receipt"]=f"repo://{repo['name']}/{receipt_path}@{repo['default_branch']}"
            clean["observed"]={"reported_status":claimed,"reported_at":receipt["reported_at"],"receipt_path":resolved_path or receipt_path}
            dump_yaml(path,clean)

        if sync_state!="SYNCED": expected_non_ready=True

    if args.apply: _refresh_traceability(fdir,load_work_packages(fdir))
    raise SystemExit(EXIT_EXPECTED_NON_READY if expected_non_ready else EXIT_OK)

if __name__=="__main__": main()
