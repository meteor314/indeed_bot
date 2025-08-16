from __future__ import annotations

from typing import List


def paginate_urls(base_url: str, start: int, end: int, step: int = 10) -> List[str]:
    """Build Indeed pagination URLs from start..end inclusive with a step.

    Example: base_url + &start=0, 10, 20, ...
    """
    urls: List[str] = []
    i = int(start)
    end = int(end)
    step = max(int(step), 1)
    while i <= end:
        urls.append(f"{base_url}&start={i}")
        i += step
    return urls
