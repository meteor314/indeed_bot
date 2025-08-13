from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Optional
import os

from camoufox.sync_api import Camoufox

from app.models import AppConfig
from app.utils import domain_for_language


LOGIN_URL_TMPL = "https://secure.indeed.com/auth?hl={hl}"


def _first(sel_list, page):
    for sel in sel_list:
        try:
            el = page.query_selector(sel)
            if el:
                return el
        except Exception:
            continue
    return None


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Login to Indeed and print PPID token (cookie)")
    p.add_argument("--config", default="config.yaml", help="Path to config.yaml (for user_data_dir/language)")
    p.add_argument("--email", default=None, help="Indeed account email (or env INDEED_EMAIL)")
    p.add_argument("--password", default=None, help="Indeed account password (or env INDEED_PASSWORD)")
    p.add_argument("--wait", type=int, default=180, help="Max seconds to wait for login detection")
    args = p.parse_args(argv)

    cfg = AppConfig.load(args.config)
    user_data_dir = cfg.camoufox.user_data_dir
    language = (cfg.camoufox.language or "us").lower()
    hl = "en" if language in ("en", "us", "uk") else language

    with Camoufox(user_data_dir=user_data_dir, persistent_context=True) as browser:
        page = browser.new_page()
        # Navigate to login
        page.goto(LOGIN_URL_TMPL.format(hl=hl))
        page.wait_for_load_state("domcontentloaded")

        email = args.email or os.getenv("INDEED_EMAIL")
        password = args.password or os.getenv("INDEED_PASSWORD")

        if email and password:
            # Best-effort auto-fill. Selectors may change; falls back silently if not found.
            email_el = _first([
                'input[type="email"]',
                'input[name="email"]',
                'input#login-email-input',
            ], page)
            if email_el:
                try:
                    email_el.fill("")
                    email_el.type(email)
                except Exception:
                    pass

            pw_el = _first([
                'input[type="password"]',
                'input[name="password"]',
                'input#login-password-input',
            ], page)
            if pw_el:
                try:
                    pw_el.fill("")
                    pw_el.type(password)
                except Exception:
                    pass

            submit_el = _first([
                'button[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Se connecter")',
                'button:has-text("Connexion")',
                'button:has-text("Log in")',
            ], page)
            if submit_el:
                try:
                    submit_el.click()
                except Exception:
                    pass

        # Poll for PPID cookie
        deadline = time.time() + max(1, int(args.wait))
        ppid_val = None
        cookies_out = []
        while time.time() < deadline:
            time.sleep(3)
            cookies = page.context.cookies()
            cookies_out = [c for c in cookies if "indeed" in (c.get("domain") or "")]
            ppid = next((c for c in cookies if c.get("name") == "PPID"), None)
            if ppid:
                ppid_val = ppid.get("value")
                break

        # Print JSON result to stdout
        result = {
            "ppid": ppid_val,
            "cookies": cookies_out,
            "success": bool(ppid_val),
        }
        print(json.dumps(result, indent=2))
        return 0 if ppid_val else 1


if __name__ == "__main__":
    raise SystemExit(main())
