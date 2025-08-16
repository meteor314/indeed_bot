from __future__ import annotations

import time


def ensure_ppid_cookie(page, language: str | None, wait_seconds: int = 120) -> bool:
    """Ensure the Indeed PPID cookie exists for the current context.

    If missing, redirect to login and wait up to wait_seconds for manual login.
    Returns True if cookie is present (before or after wait), else False.
    """
    cookies = page.context.cookies()
    ppid_cookie = next((cookie for cookie in cookies if cookie.get('name') == 'PPID'), None)
    if ppid_cookie:
        return True

    print("Token not found, please log in to Indeed first.")
    print("Redirecting to login page...")
    print("After logging in, close the tab or just wait; the bot will continue if it detects the cookie.")

    hl = "en" if str(language).lower() in ("en", "us", "uk") else str(language).lower()
    page.goto("https://secure.indeed.com/auth?hl=" + hl)

    # Poll for cookie up to wait_seconds
    deadline = time.time() + max(wait_seconds, 1)
    while time.time() < deadline:
        time.sleep(3)
        cookies = page.context.cookies()
        ppid_cookie = next((cookie for cookie in cookies if cookie.get('name') == 'PPID'), None)
        if ppid_cookie:
            return True
    return False
