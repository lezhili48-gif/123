from app.services.dedup import is_duplicate


def test_dedup_by_doi():
    c = {"doi": "10.1/x", "title": "X", "year": 2020, "first_author": "a"}
    e = [{"doi": "10.1/x", "title": "Y", "year": 2021, "first_author": "b"}]
    assert is_duplicate(c, e)


def test_dedup_fuzzy():
    c = {"doi": "", "title": "Biochar effects on soil carbon", "year": 2021, "first_author": "Lee"}
    e = [{"doi": "", "title": "Biochar effect on soil carbon", "year": 2021, "first_author": "lee"}]
    assert is_duplicate(c, e)
