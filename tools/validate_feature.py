from __future__ import annotations
import sys
from governance_lib import ROOT, load_feature, load_work_packages, validate_jsonschema, index_registry, contract_catalog, load_yaml

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_feature.py <feature-dir-or-id>")
    fdir, feature = load_feature(sys.argv[1])
    errors = []
    errors += [f"feature.yaml {e}" for e in validate_jsonschema(feature, ROOT / "schemas/feature.schema.json")]

    repos = index_registry("repositories", "repository_id")
    contracts = contract_catalog()
    participant_repos = {p["repository_id"] for p in feature.get("participants", [])}
    for rid in participant_repos:
        if rid not in repos:
            errors.append(f"unregistered participant repository: {rid}")

    change_ids = [c["id"] for c in feature.get("global_changes", [])]
    if len(change_ids) != len(set(change_ids)):
        errors.append("duplicate global_change id")

    for c in feature.get("contracts", []) or []:
        cid = c["contract_id"]
        if cid not in contracts:
            errors.append(f"unregistered contract: {cid}")
        if c["provider_repository"] not in participant_repos:
            errors.append(f"contract provider not participant: {c['provider_repository']}")
        for rid in c.get("consumer_repositories", []):
            if rid not in participant_repos:
                errors.append(f"contract consumer not participant: {rid}")

    wps = load_work_packages(fdir)
    declared = set(feature.get("work_packages", []))
    actual = set(wps)
    if declared != actual:
        errors.append(f"work package set mismatch declared={sorted(declared)} actual={sorted(actual)}")

    for wid, wp in wps.items():
        wp_for_schema = {k:v for k,v in wp.items() if k != "_path"}
        errors += [f"{wp['_path']} {e}" for e in validate_jsonschema(wp_for_schema, ROOT / "schemas/work-package.schema.json")]
        if wp["feature_id"] != feature["feature_id"]:
            errors.append(f"{wid}: feature_id mismatch")
        if wp["repository_id"] not in participant_repos:
            errors.append(f"{wid}: repository not participant")
        unknown = set(wp.get("global_change_ids", [])) - set(change_ids)
        if unknown:
            errors.append(f"{wid}: unknown global changes {sorted(unknown)}")

    roadmap = load_yaml(fdir / "roadmap.yaml")
    ids = [i["id"] for i in roadmap.get("items", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate roadmap item id")
    known = set(ids)
    for item in roadmap.get("items", []):
        for dep in item.get("depends_on", []):
            if dep not in known:
                errors.append(f"{item['id']}: unknown dependency {dep}")
        for wid in item.get("work_packages", []) or []:
            if wid not in actual:
                errors.append(f"{item['id']}: unknown work package {wid}")
        if item.get("status") == "BLOCKED" and not item.get("blocked_by"):
            errors.append(f"{item['id']}: BLOCKED requires blocked_by")

    if errors:
        print("FEATURE INVALID")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)
    print("FEATURE VALID")
    print(f"feature_id={feature['feature_id']}")
    print(f"participants={len(participant_repos)}")
    print(f"global_changes={len(change_ids)}")
    print(f"work_packages={len(wps)}")
    print(f"contracts={len(feature.get('contracts', []) or [])}")

if __name__ == "__main__":
    main()
