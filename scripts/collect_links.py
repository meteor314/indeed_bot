from __future__ import annotations

import json
import sys
import time
from typing import List

from camoufox.sync_api import Camoufox

from app.models import AppConfig
from app.utils import domain_for_language, collect_indeed_apply_links, paginate_urls


def main() -> int:
    cfg = AppConfig.load()
    language = cfg.camoufox.language
    base_url = cfg.search.base_url
    start = cfg.search.start
    end = cfg.search.end

    urls: List[str] = paginate_urls(base_url, start, end)

    proxy_kwargs = {}
    if getattr(cfg.camoufox, "proxy_server", None):
        proxy_conf = {"server": cfg.camoufox.proxy_server}
        if getattr(cfg.camoufox, "proxy_username", None):
            proxy_conf["username"] = cfg.camoufox.proxy_username
        if getattr(cfg.camoufox, "proxy_password", None):
            proxy_conf["password"] = cfg.camoufox.proxy_password
        proxy_kwargs["proxy"] = proxy_conf

    with Camoufox(user_data_dir=cfg.camoufox.user_data_dir, persistent_context=True, **proxy_kwargs) as browser:
        page = browser.new_page()
        page.goto("https://" + domain_for_language(language))

        # Require session
        cookies = page.context.cookies()
        if not any(c.get("name") == "PPID" for c in cookies):
            print("Not logged in. Please run scripts/get_token.py first.", file=sys.stderr)
            return 1

        all_links: List[str] = []
        for url in urls:
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(5)
            try:
                links = collect_indeed_apply_links(page, language)
                all_links.extend(links)
            except Exception:
                continue

    print(json.dumps({"count": len(all_links), "links": all_links}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
