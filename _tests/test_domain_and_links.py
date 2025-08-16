from __future__ import annotations

import pytest

from app.utils.indeed import domain_for_language, collect_indeed_apply_links, click_and_wait
from _tests.conftest import FakeElement


def test_domain_for_language_cases():
    assert domain_for_language(None) == "www.indeed.com"
    assert domain_for_language("") == "www.indeed.com"
    assert domain_for_language("en") == "www.indeed.com"
    assert domain_for_language("us") == "www.indeed.com"
    assert domain_for_language("uk") == "uk.indeed.com"
    assert domain_for_language("fr") == "fr.indeed.com"
    assert domain_for_language("de") == "de.indeed.com"


def test_collect_indeed_apply_links_prefix_and_filter(fake_page):
    # fake_page has 4 cards: two valid (one relative, one absolute), one None href, one non-apply
    links = collect_indeed_apply_links(fake_page, language="us")
    assert links == [
        "https://www.indeed.com/viewjob?jk=abc",
        "https://www.indeed.com/viewjob?jk=def",
    ]


def test_click_and_wait_marks_clicked(monkeypatch):
    elem = FakeElement()
    # Avoid sleeping during test
    monkeypatch.setattr("app.utils.indeed.time.sleep", lambda s: None)
    click_and_wait(elem, timeout=0.1)
    assert elem.clicked is True
