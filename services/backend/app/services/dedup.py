from difflib import SequenceMatcher


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def is_duplicate(candidate: dict, existing: list[dict]) -> bool:
    c_doi = (candidate.get("doi") or "").lower().strip()
    for item in existing:
        e_doi = (item.get("doi") or "").lower().strip()
        if c_doi and e_doi and c_doi == e_doi:
            return True
        if candidate.get("year") and item.get("year") and str(candidate.get("year")) == str(item.get("year")):
            title_score = similar(candidate.get("title", ""), item.get("title", ""))
            c_first = (candidate.get("first_author") or "").lower()
            e_first = (item.get("first_author") or "").lower()
            if title_score > 0.92 and c_first and c_first == e_first:
                return True
    return False
