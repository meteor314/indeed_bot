from __future__ import annotations

from typing import Sequence


def _log(logger, level: str, msg: str) -> None:
    if logger is None:
        print(f"[selector:{level}] {msg}")
        return
    try:
        getattr(logger, level, logger.info)(msg)
    except Exception:
        print(f"[selector:{level}] {msg}")


def find_first(page, selectors: Sequence[str], *, visible_only: bool = False, logger=None, desc: str | None = None):
    """Try a list of selectors and return the first matching element.

    - Logs each attempt and which selector matched.
    - If visible_only=True, ignores elements that are not visible.
    - Returns the element or None.
    """
    label = f"{desc}: " if desc else ""
    for sel in selectors:
        try:
            el = page.query_selector(sel)
        except Exception as e:
            _log(logger, "warning", f"{label}query_selector failed for '{sel}': {e}")
            continue
        if not el:
            _log(logger, "debug", f"{label}no match for '{sel}'")
            continue
        if visible_only:
            try:
                if not el.is_visible():
                    _log(logger, "debug", f"{label}matched but not visible: '{sel}'")
                    continue
            except Exception:
                pass
        _log(logger, "info", f"{label}matched selector: '{sel}'")
        return el
    _log(logger, "warning", f"{label}no selectors matched from list of {len(selectors)}")
    return None


def find_all(page, selector: str, *, logger=None, desc: str | None = None):
    """Return all matches for a selector with debug log of count."""
    label = f"{desc}: " if desc else ""
    try:
        items = page.query_selector_all(selector)
        _log(logger, "info", f"{label}found {len(items)} elements for '{selector}'")
        return items
    except Exception as e:
        _log(logger, "error", f"{label}query_selector_all failed for '{selector}': {e}")
        return []


def click_first(page, selectors: Sequence[str], *, timeout_ms: int = 5000, logger=None, desc: str | None = None) -> bool:
    """Find first element using selectors and click it with timeout; returns True if clicked."""
    el = find_first(page, selectors, logger=logger, desc=desc)
    if not el:
        return False
    try:
        el.click(timeout=max(0, int(timeout_ms)))
        _log(logger, "info", f"{desc or 'element'} clicked with timeout {timeout_ms}ms")
        return True
    except Exception as e:
        _log(logger, "warning", f"click with timeout failed: {e}; trying without timeout")
        try:
            el.click()
            _log(logger, "info", f"{desc or 'element'} clicked without timeout")
            return True
        except Exception as e2:
            _log(logger, "error", f"click failed: {e2}")
            return False
