from __future__ import annotations

import time
from typing import List

from camoufox.sync_api import Camoufox

from app.models import AppConfig
from app.utils import (
    setup_logger,
    domain_for_language,
    collect_indeed_apply_links,
    apply_to_job,
)


"""
Minimal Indeed Auto-Apply Bot
-----------------------------
- Uses the modular utilities in app/.
- Single-pass: only visits the configured base_url (no pagination).
- Applies to the jobs found on that page.

Run:
  uv run python indeed_bot_min.py
"""


def main(config_path: str = "config.yaml") -> None:
    cfg = AppConfig.load(config_path)
    user_data_dir = cfg.camoufox.user_data_dir
    language = cfg.camoufox.language

    with Camoufox(user_data_dir=user_data_dir, persistent_context=True) as browser:
        logger = setup_logger()
        page = browser.new_page()

        # Open correct Indeed domain
        base_domain = domain_for_language(language)
        page.goto("https://" + base_domain)

        # Require login cookie
        cookies = page.context.cookies()
        ppid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'PPID'), None)
        if not ppid_cookie:
            print("Token not found, please log in to Indeed first.")
            print("Redirecting to login page...")
            print("After logging in, close the browser and run this script again.")
            hl = "en" if str(language).lower() in ("en", "us", "uk") else str(language).lower()
            page.goto("https://secure.indeed.com/auth?hl=" + hl)
            time.sleep(120)  # short wait for manual login, then exit
            return

        # Single or multiple URL(s) visit (no pagination)
        url_list: List[str]
        if getattr(cfg.search, "base_urls", None):
            url_list = list(cfg.search.base_urls or [])
        else:
            url_list = [cfg.search.base_url]

        for base_url in url_list:
            print(f"Visiting URL: {base_url}")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            print("Waiting for page to settle (Cloudflare, etc). If a button appears, click it manually.")
            time.sleep(10)

            try:
                links: List[str] = collect_indeed_apply_links(page, language)
                print(f"Found {len(links)} Indeed Apply jobs on this page.")
            except Exception as e:
                print("Error extracting jobs:", e)
                links = []

            for job_url in links:
                print(f"Applying to: {job_url}")
                success = apply_to_job(browser, job_url, language, logger)
                if not success:
                    logger.error(f"Failed to apply to {job_url}")
                time.sleep(5)


if __name__ == "__main__":
    main()
