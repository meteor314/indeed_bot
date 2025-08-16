from __future__ import annotations

import itertools
import pytest

from app.utils.login import ensure_ppid_cookie
from _tests.conftest import FakePage


def test_ensure_ppid_cookie_present_immediate():
    page = FakePage(cookies=[{"name": "PPID", "value": "token"}])
    assert ensure_ppid_cookie(page, language="us", wait_seconds=1) is True


def test_ensure_ppid_cookie_missing_times_out(monkeypatch):
    # No cookies ever appear, ensure fast timeout using monkeypatch on time
    page = FakePage(cookies=[])

    times = iter([0, 2])  # start < deadline, then > deadline
    monkeypatch.setattr("app.utils.login.time.time", lambda: next(times, 2.5))
    monkeypatch.setattr("app.utils.login.time.sleep", lambda s: None)
    assert ensure_ppid_cookie(page, language="us", wait_seconds=1) is False


def test_ensure_ppid_cookie_appears_during_wait(monkeypatch):
    # Start with no PPID, then PPID appears on second poll
    page = FakePage(cookies=[])

    # mutable cookies storage to simulate appearance
    cookies_state = [[], [{"name": "PPID", "value": "x"}]]

    def cookies_flip():
        # return first non-empty snapshot until exhausted
        if cookies_state:
            snap = cookies_state.pop(0)
            return snap
        return [{"name": "PPID", "value": "x"}]

    monkeypatch.setattr(page.context, "cookies", cookies_flip)

    # Progress time: first call inside window, second also inside -> PPID found
    times = iter([0, 0.5, 0.8])
    monkeypatch.setattr("app.utils.login.time.time", lambda: next(times, 0.8))
    monkeypatch.setattr("app.utils.login.time.sleep", lambda s: None)

    assert ensure_ppid_cookie(page, language="us", wait_seconds=2) is True
