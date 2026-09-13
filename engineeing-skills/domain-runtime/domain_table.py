"""Strict shared Markdown table contract for domain intent and quality ledgers."""
import re
def validate_table(path, heading, required, prefix):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^##\s+" + re.escape(heading) + r"\s*$\n?(.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    lines = [x.strip() for x in (m.group(1) if m else "").splitlines() if x.strip().startswith("|")]
    errors = []
    def err(code, detail): errors.append({"code": prefix+"_"+code, "detail": detail})
    cells = lambda x: [v.strip().strip("`") for v in x.strip("|").split("|")]
    if len(lines) < 3:
        err("ROWS_MISSING", heading); return errors
    header = cells(lines[0])
    if len(set(header)) != len(header) or any(x not in header for x in required):
        err("COLUMNS_MISSING", str(required))
    separator = cells(lines[1])
    if len(separator) != len(header) or not all(re.fullmatch(r":?-{3,}:?", x) for x in separator):
        err("SEPARATOR_INVALID", heading)
    ids = []
    for index, line in enumerate(lines[2:], 1):
        values = cells(line)
        if len(values) != len(header):
            err("ROW_SHAPE_INVALID", str(index)); continue
        row = dict(zip(header, values)); ids.append(row.get("Change ID", ""))
        bad = [k for k in required if not row.get(k) or re.search(r"<[^>]+>|\bTBD\b|\?\?\?", row.get(k, ""), re.I)]
        if bad: err("ROW_INCOMPLETE", f"row={index} fields={bad}")
    if len(ids) != len(set(ids)): err("DUPLICATE_CHANGE_ID", str(ids))
    return errors
