from __future__ import annotations

import argparse
import sys
import time
from typing import List, Optional

from camoufox.sync_api import Camoufox

from app.models import AppConfig
from app.utils import (
    setup_logger,
    domain_for_language,
    collect_indeed_apply_links,
    apply_to_job,
    paginate_urls,
)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Collect Indeed Apply links and apply to them")
    p.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    p.add_argument("--single", default=None, help="Apply to a single job URL (skips search)")
    p.add_argument("--max", type=int, default=0, help="Max number of jobs to apply to (0 = all)")
    p.add_argument("--delay", type=float, default=5.0, help="Delay between job applications (seconds)")
    args = p.parse_args(argv)

    cfg = AppConfig.load(args.config)
    language = cfg.camoufox.language

    proxy_kwargs = {}
    if getattr(cfg.camoufox, "proxy_server", None):
        proxy_conf = {"server": cfg.camoufox.proxy_server}
        if getattr(cfg.camoufox, "proxy_username", None):
            proxy_conf["username"] = cfg.camoufox.proxy_username
        if getattr(cfg.camoufox, "proxy_password", None):
            proxy_conf["password"] = cfg.camoufox.proxy_password
        proxy_kwargs["proxy"] = proxy_conf

    with Camoufox(user_data_dir=cfg.camoufox.user_data_dir, persistent_context=True, **proxy_kwargs) as browser:
        logger = setup_logger()
        page = browser.new_page()

        # Ensure session by visiting domain and checking PPID
        page.goto("https://" + domain_for_language(language))
        cookies = page.context.cookies()
        if not any(c.get("name") == "PPID" for c in cookies):
            print("Not logged in. Please run scripts/get_token.py to login and obtain a session.", file=sys.stderr)
            return 1

        job_links: List[str] = []
        if args.single:
            job_links = [args.single]
        else:
            base_url = cfg.search.base_url
            start = cfg.search.start
            end = cfg.search.end
            urls: List[str] = paginate_urls(base_url, start, end)
            for url in urls:
                print(f"Visiting URL: {url}")
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(10)
                try:
                    links = collect_indeed_apply_links(page, language)
                    print(f"Found {len(links)} Indeed Apply jobs on this page.")
                    job_links.extend(links)
                except Exception as e:
                    print(f"Error extracting jobs on {url}: {e}")
                time.sleep(2)

        # Apply
        count = 0
        limit = int(args.__dict__["max"]) if args.__dict__["max"] else 0
        for job_url in job_links:
            print(f"Applying to: {job_url}")
            ok = apply_to_job(browser, job_url, language, logger)
            if not ok:
                logger.error(f"Failed to apply to {job_url}")
            count += 1
            if limit and count >= limit:
                break
            time.sleep(max(0.0, float(args.delay)))

        print(f"Completed applying to {count} job(s)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
