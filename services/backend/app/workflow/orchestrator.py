import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from openai import OpenAI
from playwright.sync_api import sync_playwright
from app.core.config import get_settings
from app.services.allowlist import host_allowed


TAKEOVER_KEYWORDS = ["captcha", "verify", "sign in", "login", "terms"]


def detect_takeover(url: str, title: str, text: str) -> bool:
    s = f"{url} {title} {text}".lower()
    return any(k in s for k in TAKEOVER_KEYWORDS)


def run_workflow(project: dict, run_id: int, update_cb, wait_for_approval):
    settings = get_settings()
    allowlist = project.get("allowlist") or settings.allowlist
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    screenshot_path = settings.data_dir / "screenshots" / f"run_{run_id}_0.png"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="services/backend/playwright-profile",
            headless=False,
            accept_downloads=True,
        )
        page = context.new_page()
        start_url = "https://www.webofscience.com" if project["source"] == "wos" else "https://www.scopus.com"
        if not host_allowed(start_url, allowlist):
            update_cb("FAILED", f"Start URL blocked by allowlist: {start_url}", None)
            context.close()
            return
        page.goto(start_url)
        page.screenshot(path=str(screenshot_path), full_page=True)
        update_cb("RUNNING", "Browser opened", str(screenshot_path))

        for step in range(1, 6):
            page.wait_for_timeout(1000)
            current = page.url
            if not host_allowed(current, allowlist):
                update_cb("FAILED", f"Navigation blocked by allowlist: {current}", str(screenshot_path))
                break
            text = page.content()[:2000]
            if detect_takeover(current, page.title(), text):
                update_cb("NEED_TAKEOVER", "Login/captcha/terms detected. Please takeover.", str(screenshot_path))
                wait_for_approval()
                update_cb("RUNNING", "Resumed after takeover", str(screenshot_path))
            if client:
                prompt = f"Site={project['source']}, query={project['query']}, year_range={project.get('year_range','')}. Suggest one next action only."
                _ = client.responses.create(model=settings.model_text, input=prompt)
            page.screenshot(path=str(settings.data_dir / "screenshots" / f"run_{run_id}_{step}.png"), full_page=True)
            update_cb("RUNNING", f"Step {step} executed", str(settings.data_dir / "screenshots" / f"run_{run_id}_{step}.png"))

        export_file = settings.data_dir / "exports" / f"run_{run_id}_export.ris"
        export_file.write_text("TY  - JOUR\nTI  - Placeholder export\nER  -\n", encoding="utf-8")
        digest = hashlib.sha256(export_file.read_bytes()).hexdigest()
        audit_file = settings.data_dir / "audit" / f"run_{run_id}.json"
        audit_file.write_text(json.dumps({"run_id": run_id, "export_file": str(export_file), "sha256": digest, "at": datetime.utcnow().isoformat()}, indent=2), encoding="utf-8")
        update_cb("COMPLETED", f"Run completed, export hash={digest[:12]}", str(settings.data_dir / "screenshots" / f"run_{run_id}_5.png"))
        context.close()
