from app.services.ris_parser import parse_ris


def test_parse_ris_basic():
    content = "TY  - JOUR\nTI  - A title\nDO  - 10.1/abc\nPY  - 2024\nAU  - Alice\nER  -\n"
    recs = parse_ris(content)
    assert len(recs) == 1
    assert recs[0]["title"] == "A title"
    assert recs[0]["doi"] == "10.1/abc"
