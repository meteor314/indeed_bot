from __future__ import annotations

import types
import pytest

from app.utils.indeed import apply_to_job


class LoggerStub:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.errors = []

    def info(self, msg):
        self.infos.append(msg)

    def warning(self, msg):
        self.warnings.append(msg)

    def error(self, msg):
        self.errors.append(msg)


class ApplyFlowPage:
    """Finite-state fake page to drive apply_to_job() happy path."""

    def __init__(self):
        self._state = "start"
        self._url = "https://job.example/apply"

    # Minimal API used by apply_to_job
    @property
    def url(self):
        return self._url

    def goto(self, url: str):
        self._url = url

    def wait_for_load_state(self, _state: str):
        return None

    def query_selector(self, sel: str):
        # Apply button step
        if self._state == "start":
            if sel in (
                'button:has(span[class*="css-1ebo7dz"])',
                'button:visible:has-text("Postuler")',
                'button:visible:has-text("Apply")',
            ):
                return _Clickable(lambda: self._advance("resume"))
            return None
        # Resume step: expose resume card
        if self._state == "resume":
            if sel == '[data-testid="FileResumeCardHeader-title"]':
                return _Clickable(lambda: None)
            return None
        return None

    def query_selector_all(self, sel: str):
        # Resume step: show continue button
        if self._state == "resume" and sel == 'button:visible':
            return [_TextButton("Continue", lambda: self._advance("submit"))]
        # Submit step: show submit button last
        if self._state == "submit" and sel == 'button:visible':
            return [_TextButton("Submit", lambda: self._advance("done"))]
        return []

    def close(self):
        return None

    # helpers
    def _advance(self, next_state: str):
        self._state = next_state
        if next_state == "done":
            self._url = self._url + "#submitted"


class _Clickable:
    def __init__(self, on_click):
        self._on_click = on_click

    def click(self, timeout: int | None = None):
        self._on_click()

    def evaluate_handle(self, _):
        return self


class _TextButton(_Clickable):
    def __init__(self, text: str, on_click):
        super().__init__(on_click)
        self._text = text

    def inner_text(self):
        return self._text

    def get_attribute(self, name: str):
        return None

    def is_visible(self):
        return True


class FakeBrowser:
    def __init__(self):
        self._page = ApplyFlowPage()

    def new_page(self):
        # return a fresh page per call
        self._page = ApplyFlowPage()
        return self._page


def test_apply_to_job_happy_path(monkeypatch):
    # Avoid real sleeps
    monkeypatch.setattr("app.utils.indeed.time.sleep", lambda s: None)
    browser = FakeBrowser()
    logger = LoggerStub()
    ok = apply_to_job(browser, "https://job.example/view", language="us", logger=logger)
    assert ok is True
    assert any("Applied successfully" in msg for msg in logger.infos)


class NoApplyButtonPage(ApplyFlowPage):
    def query_selector(self, sel: str):
        return None


class FailBrowser:
    def new_page(self):
        return NoApplyButtonPage()


def test_apply_to_job_no_apply_button(monkeypatch):
    monkeypatch.setattr("app.utils.indeed.time.sleep", lambda s: None)
    browser = FailBrowser()
    logger = LoggerStub()
    ok = apply_to_job(browser, "https://job.example/view", language="us", logger=logger)
    assert ok is False
    assert any("No Indeed Apply button" in msg for msg in logger.warnings)
