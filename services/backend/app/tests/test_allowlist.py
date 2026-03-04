from app.services.allowlist import host_allowed


def test_allowlist_wildcard():
    assert host_allowed("https://www.scopus.com/search", ["*.scopus.com"])
    assert not host_allowed("https://evil.com", ["*.scopus.com"])
