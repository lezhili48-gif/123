
def parse_ris(content: str) -> list[dict]:
    records: list[dict] = []
    current: dict = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        if line.startswith("ER"):
            if current:
                records.append(current)
            current = {}
            continue
        if "  - " not in line:
            continue
        tag, value = line.split("  - ", 1)
        tag = tag.strip()
        value = value.strip()
        mapping = {
            "TI": "title",
            "DO": "doi",
            "PY": "year",
            "JO": "journal",
            "AB": "abstract",
            "AU": "authors",
        }
        key = mapping.get(tag, tag.lower())
        if key == "authors":
            current.setdefault("authors", []).append(value)
        else:
            current[key] = value
    if current:
        records.append(current)
    return records
