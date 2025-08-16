from __future__ import annotations

import time
from typing import List, Optional
from .selector import find_first, find_all, click_first


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
    job_cards = find_all(page, 'div[data-testid="slider_item"]', desc="job cards")
    for card in job_cards:
        indeed_apply = None
        try:
            indeed_apply = card.query_selector('[data-testid="indeedApply"]')
        except Exception:
            indeed_apply = None
        if indeed_apply:
            link = None
            try:
                link = card.query_selector('a.jcs-JobTitle')
            except Exception:
                link = None
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
        apply_selectors = [
            'button:has(span[class*="css-1ebo7dz"])',
            'button:visible:has-text("Postuler")',
            'button:visible:has-text("Apply")',
        ]
        clicked = False
        for _ in range(20):
            # attempt clicking using selector helper
            if click_first(page, apply_selectors, timeout_ms=5000, logger=logger, desc="apply button"):
                clicked = True
                break
            # fallback: scan visible buttons heuristically
            btns = find_all(page, 'button:visible', logger=logger, desc="visible buttons")
            apply_candidate = None
            for btn in btns:
                label = (btn.get_attribute("aria-label") or "").lower()
                text = (btn.inner_text() or "").lower()
                if any(x in label for x in ("close", "cancel", "fermer", "annuler")):
                    continue
                if "postuler" in text or "apply" in text:
                    apply_candidate = btn
                    break
            if apply_candidate:
                click_and_wait(apply_candidate, 5)
                clicked = True
                break
            time.sleep(0.5)
        if clicked:
            # proceed to wizard
            pass
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
            resume_card = find_first(page, ['[data-testid="FileResumeCardHeader-title"]'], logger=logger, desc="resume card")
            if resume_card:
                # Click the resume card (or its parent if needed)
                try:
                    resume_card.click()
                except Exception:
                    parent = resume_card.evaluate_handle('node => node.parentElement')
                    if parent:
                        parent.click()
                time.sleep(1)
                if click_first(page, ['button:visible:has-text("Continuer")', 'button:visible:has-text("Continue")'], timeout_ms=3000, logger=logger, desc="continue button"):
                    # go to next step
                    time.sleep(0.5)
                    continue  # go to next step
                else:
                    # Fallback: scan visible buttons by text
                    btns = find_all(page, 'button:visible', logger=logger, desc="visible buttons")
                    for btn in btns:
                        text = (btn.inner_text() or "").lower()
                        if "continuer" in text or "continue" in text:
                            click_and_wait(btn, 3)
                            time.sleep(0.5)
                            break
                    # proceed to next loop iteration regardless; if not advanced, the next checks will handle

            # try to find a submit button (dynamic text)
            # Try language-specific submit selectors first
            if click_first(
                page,
                [
                    'button:visible:has-text("Déposer ma candidature")',
                    'button:visible:has-text("Soumettre")',
                    'button:visible:has-text("Submit")',
                    'button:visible:has-text("Apply")',
                    'button:visible:has-text("Bewerben")',
                    'button:visible:has-text("Postular")',
                ],
                timeout_ms=3000,
                logger=logger,
                desc="submit button",
            ):
                logger.info(f"Applied successfully to {job_url}")
                break
            else:
                # Fallback: scan visible buttons by text and click
                btns = find_all(page, 'button:visible', logger=logger, desc="visible buttons")
                submit_btn = None
                for btn in btns:
                    text = (btn.inner_text() or "").lower()
                    if (
                        "déposer ma candidature" in text
                        or "soumettre" in text
                        or "submit" in text
                        or "apply" in text
                        or "bewerben" in text
                        or "postular" in text
                    ):
                        submit_btn = btn
                        break
                if not submit_btn and btns:
                    submit_btn = btns[-1]
                if submit_btn:
                    click_and_wait(submit_btn, 3)
                    logger.info(f"Applied successfully to {job_url}")
                    break

            # fallback: try to find a visible and enabled button to continue (other steps)
            btn = find_first(
                page,
                ['button[type="button"]:not([aria-disabled="true"])', 'button[type="submit"]:not([aria-disabled="true"])'],
                logger=logger,
                desc="generic continue/submit",
            )
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
