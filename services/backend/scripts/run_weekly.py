import requests

base = "http://127.0.0.1:8000"
projects = requests.get(f"{base}/api/projects", timeout=10).json()
if not projects:
    print("No projects found")
else:
    p = projects[0]
    r = requests.post(f"{base}/api/runs/{p['id']}/start", timeout=30).json()
    print("Triggered run", r)
