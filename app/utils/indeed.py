from __future__ import annotations

import time
from typing import List, Optional


def domain_for_language(lang: Optional[str]) -> str:
    """Return the appropriate Indeed domain for a given language/locale code.

    Examples:
      - 'en' or 'us' -> 'www.indeed.com'
      - 'uk'         -> 'uk.indeed.com'
      - 'fr'         -> 'fr.indeed.com'
    Fallback: f"{lang}.indeed.com"
    """
    if not lang:
        return "www.indeed.com"
    lang = str(lang).lower()
    if lang in ("en", "us"):
        return "www.indeed.com"
    if lang == "uk":
        return "uk.indeed.com"
    return f"{lang}.indeed.com"


def collect_indeed_apply_links(page, language: Optional[str]) -> List[str]:
    """Collect all 'Indeed Apply' job links from the current search result page."""
    links: List[str] = []
    job_cards = page.query_selector_all('div[data-testid="slider_item"]')
    for card in job_cards:
        indeed_apply = card.query_selector('[data-testid="indeedApply"]')
        if indeed_apply:
            link = card.query_selector('a.jcs-JobTitle')
            if link:
                job_url = link.get_attribute('href')
                if job_url:
                    if job_url.startswith('/'):
                        job_url = f"https://{domain_for_language(language)}{job_url}"
                    links.append(job_url)
    return links


def click_and_wait(element, timeout: float = 5.0) -> None:
    if element:
        try:
            # Convert seconds to ms for Playwright's timeout parameter
            element.click(timeout=int(max(timeout, 0) * 1000))
        except Exception:
            # Best-effort fallback without explicit timeout
            try:
                element.click()
            except Exception:
                # Swallow click failures at this stage; caller flow will handle by timeouts/next attempts
                return
        time.sleep(timeout)


def apply_to_job(browser, job_url: str, language: Optional[str], logger) -> bool:
    """Open a new tab, apply to the job, log the result, and close the tab."""
    page = browser.new_page()
    try:
        page.goto(job_url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        # Try to find the apply button using robust, language-agnostic selectors
        apply_btn = None
        for _ in range(20):
            # 1. Try button with a span with the unique Indeed Apply class (often css-1ebo7dz)
            apply_btn = page.query_selector('button:has(span[class*="css-1ebo7dz"])')
            # 2. Fallbacks: buttons with language-specific text
            if not apply_btn:
                apply_btn = page.query_selector('button:visible:has-text("Postuler")')
            if not apply_btn:
                apply_btn = page.query_selector('button:visible:has-text("Apply")')
            # 3. Fallback: first visible button on the page (avoid close/cancel if possible)
            if not apply_btn:
                btns = page.query_selector_all('button:visible')
                for btn in btns:
                    label = (btn.get_attribute("aria-label") or "").lower()
                    text = (btn.inner_text() or "").lower()
                    if any(x in label for x in ("close", "cancel", "fermer", "annuler")):
                        continue
                    if "postuler" in text or "apply" in text or btn.is_visible():
                        apply_btn = btn
                        break
            if apply_btn:
                break
            time.sleep(0.5)
        if apply_btn:
            click_and_wait(apply_btn, 5)
        else:
            logger.warning(f"No Indeed Apply button found for {job_url}")
            page.close()
            return False

        # add timeout for the wizard loop
        start_time = time.time()
        while True:
            if time.time() - start_time > 40:
                logger.warning(f"Timeout applying to {job_url}, closing tab and moving to next.")
                break
            current_url = page.url
            # Resume step: select resume card if present
            resume_card = page.query_selector('[data-testid="FileResumeCardHeader-title"]')
            if resume_card:
                # Click the resume card (or its parent if needed)
                try:
                    resume_card.click()
                except Exception:
                    parent = resume_card.evaluate_handle('node => node.parentElement')
                    if parent:
                        parent.click()
                time.sleep(1)
                continuer_btn = None
                btns = page.query_selector_all('button:visible')
                for btn in btns:
                    text = (btn.inner_text() or "").lower()
                    if "continuer" in text or "continue" in text:
                        continuer_btn = btn
                        break
                if continuer_btn:
                    click_and_wait(continuer_btn, 3)
                    continue  # go to next step

            # try to find a submit button (dynamic text)
            submit_btn = None
            btns = page.query_selector_all('button:visible')
            for btn in btns:
                text = (btn.inner_text() or "").lower()
                if (
                    "déposer ma candidature" in text or
                    "soumettre" in text or
                    "submit" in text or
                    "apply" in text or
                    "bewerben" in text or  # German
                    "postular" in text     # Spanish
                ):
                    submit_btn = btn
                    break
            # fallback: last visible button (often the submit)
            if not submit_btn and btns:
                submit_btn = btns[-1]
            if submit_btn:
                click_and_wait(submit_btn, 3)
                logger.info(f"Applied successfully to {job_url}")
                break

            # fallback: try to find a visible and enabled button to continue (other steps)
            btn = page.query_selector('button[type="button"]:not([aria-disabled="true"]), button[type="submit"]:not([aria-disabled="true"])')
            if btn:
                click_and_wait(btn, 3)
                if "confirmation" in page.url or "submitted" in page.url:
                    logger.info(f"Applied successfully to {job_url}")
                    break
            else:
                logger.warning(f"No continue/submit button found at {current_url}")
                break
        page.close()
        return True
    except Exception as e:
        logger.error(f"Error applying to {job_url}: {e}")
        page.close()
        return False
