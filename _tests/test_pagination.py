from __future__ import annotations

from app.utils.pagination import paginate_urls


def test_paginate_urls_basic():
    base = "https://www.indeed.com/jobs?q=python"
    out = paginate_urls(base, 0, 20, step=10)
    assert out == [
        "https://www.indeed.com/jobs?q=python&start=0",
        "https://www.indeed.com/jobs?q=python&start=10",
        "https://www.indeed.com/jobs?q=python&start=20",
    ]


def test_paginate_urls_non_multiple_step():
    base = "https://uk.indeed.com/jobs?q=qa"
    out = paginate_urls(base, 0, 5, step=2)
    assert out == [
        "https://uk.indeed.com/jobs?q=qa&start=0",
        "https://uk.indeed.com/jobs?q=qa&start=2",
        "https://uk.indeed.com/jobs?q=qa&start=4",
    ]


def test_paginate_urls_end_inclusive():
    base = "https://fr.indeed.com/jobs?q=go"
    out = paginate_urls(base, 10, 10)
    assert out == ["https://fr.indeed.com/jobs?q=go&start=10"]
