from __future__ import annotations

import types
import time
import pytest


class FakeElement:
    def __init__(self, text: str = "", aria_label: str = "", visible: bool = True):
        self._text = text
        self._aria_label = aria_label
        self._visible = visible
        self.clicked = False

    # Playwright-like API subset
    def click(self, timeout: int | None = None):
        # simulate a small delay respecting timeout if provided
        self.clicked = True
        return None

    def inner_text(self):
        return self._text

    def get_attribute(self, name: str):
        if name == "aria-label":
            return self._aria_label
        return None

    def is_visible(self):
        return self._visible

    # used in apply_to_job resume branch
    def evaluate_handle(self, js):
        # simulate parentElement.click() path
        parent = FakeElement()
        parent.click()
        return parent


class FakeNode:
    def __init__(self, attrs: dict[str, str] | None = None):
        self.attrs = attrs or {}

    def get_attribute(self, name: str):
        return self.attrs.get(name)


class FakeCard:
    def __init__(self, href: str | None, has_apply: bool = True):
        self._href = href
        self._has_apply = has_apply

    def query_selector(self, sel: str):
        if sel == '[data-testid="indeedApply"]':
            return FakeElement() if self._has_apply else None
        if sel == 'a.jcs-JobTitle':
            return FakeNode({"href": self._href})
        return None


class FakeContext:
    def __init__(self, cookies: list[dict] | None = None):
        self._cookies = cookies or []

    def cookies(self):
        return self._cookies


class FakePage:
    def __init__(self, cards: list[FakeCard] | None = None, cookies: list[dict] | None = None):
        self._cards = cards or []
        self.url = "https://example.test"
        self.context = FakeContext(cookies=cookies)

    def query_selector_all(self, sel: str):
        if sel == 'div[data-testid="slider_item"]':
            return self._cards
        if sel == 'button:visible':
            # basic visible buttons
            return [FakeElement("Apply"), FakeElement("Continue"), FakeElement("Submit")]
        return []

    def query_selector(self, sel: str):
        if sel == 'button:visible:has-text("Apply")':
            return FakeElement("Apply")
        if sel == 'button:visible:has-text("Postuler")':
            return FakeElement("Postuler")
        if sel == 'button:has(span[class*="css-1ebo7dz"])':
            return None
        return None

    # Navigations used by app.main
    def goto(self, url: str):
        self.url = url

    def wait_for_load_state(self, _state: str):
        return None


@pytest.fixture
def fake_page():
    cards = [
        FakeCard("/viewjob?jk=abc"),
        FakeCard("https://www.indeed.com/viewjob?jk=def"),
        FakeCard(None, has_apply=True),
        FakeCard("/viewjob?jk=ghi", has_apply=False),
    ]
    return FakePage(cards)
