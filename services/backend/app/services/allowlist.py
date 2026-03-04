from urllib.parse import urlparse
import fnmatch


def host_allowed(url: str, patterns: list[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(fnmatch.fnmatch(host, p.lower().replace("https://", "").replace("http://", "")) for p in patterns)
