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
    paginate_urls,
    ensure_ppid_cookie,
)


def run(config_path: str = "config.yaml") -> None:
    cfg = AppConfig.load(config_path)
    user_data_dir = cfg.camoufox.user_data_dir
    language = cfg.camoufox.language

    # Build optional proxy kwargs
    proxy_kwargs = {}
    if getattr(cfg.camoufox, "proxy_server", None):
        proxy_conf = {"server": cfg.camoufox.proxy_server}
        if getattr(cfg.camoufox, "proxy_username", None):
            proxy_conf["username"] = cfg.camoufox.proxy_username
        if getattr(cfg.camoufox, "proxy_password", None):
            proxy_conf["password"] = cfg.camoufox.proxy_password
        proxy_kwargs["proxy"] = proxy_conf

    with Camoufox(user_data_dir=user_data_dir, persistent_context=True, **proxy_kwargs) as browser:
        logger = setup_logger()
        page = browser.new_page()
        # Set reasonable default timeouts
        try:
            page.set_default_timeout(30000)  # 30s for actions
            page.set_default_navigation_timeout(45000)  # 45s for navigations
        except Exception:
            pass
        base_domain = domain_for_language(language)
        page.goto("https://" + base_domain)

        if not ensure_ppid_cookie(page, language, wait_seconds=180):
            print("Login not detected in time. Please run again after logging in.")
            return

        print("Token found, proceeding with job search...")
        # Backward compatible behavior: if base_urls not provided, paginate base_url
        if getattr(cfg.search, "base_urls", None):
            list_urls: List[str] = list(cfg.search.base_urls or [])
        else:
            base_url = cfg.search.base_url
            start = cfg.search.start
            end = cfg.search.end
            list_urls: List[str] = paginate_urls(base_url, start, end, step=10)

        def process_pages(urls: List[str]) -> List[str]:
            all_job_links: List[str] = []
            for url in urls:
                print(f"Visiting URL: {url}")
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                print("Waiting for page to load, if any cloudflare protection button appears... please click it.")
                time.sleep(10)
                try:
                    links = collect_indeed_apply_links(page, language)
                    all_job_links.extend(links)
                    print(f"Found {len(links)} Indeed Apply jobs on this page.")
                except Exception as e:
                    print("Error extracting jobs:", e)
                time.sleep(5)
            return all_job_links

        try:
            # First pass
            job_links = process_pages(list_urls)
            print(f"Total Indeed Apply jobs found: {len(job_links)}")
            for job_url in job_links:
                print(f"Applying to: {job_url}")
                success = apply_to_job(browser, job_url, language, logger)
                if not success:
                    logger.error(f"Failed to apply to {job_url}")
                time.sleep(5)

            # Second pass (as per original script)
            job_links = process_pages(list_urls)
            print(f"Total Indeed Apply jobs found: {len(job_links)}")
            for job_url in job_links:
                print(f"Applying to: {job_url}")
                success = apply_to_job(browser, job_url, language, logger)
                if not success:
                    logger.error(f"Failed to apply to {job_url}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Interrupted by user. Shutting down gracefully...")


if __name__ == "__main__":
    run()
