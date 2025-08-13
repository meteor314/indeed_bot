"""
Indeed Auto-Apply Bot
---------------------
Automates job applications on Indeed using Camoufox.

Usage:
  - Configure your search and Chrome settings in config.yaml
  - Run: python indeed_bot.py

Author: @meteor314 
License: MIT
"""
import yaml
import time
from datetime import datetime
from typing import Dict, Any
from camoufox.sync_api import Camoufox
import logging


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
camoufox_config = config.get("camoufox", {})
user_data_dir = camoufox_config.get("user_data_dir")
language = camoufox_config.get("language")


def domain_for_language(lang: str) -> str:
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


def collect_indeed_apply_links(page, language):
    """Collect all 'Indeed Apply' job links from the current search result page."""
    links = []
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


def click_and_wait(element, timeout=5):
    if element:
        element.click()
        time.sleep(timeout)


def apply_to_job(browser, job_url, language, logger):
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
            apply_btn = page.query_selector(
                'button:has(span[class*="css-1ebo7dz"])')
            # 2. Fallback: first visible button with a span containing "Postuler" or "Apply"
            if not apply_btn:
                apply_btn = page.query_selector(
                    'button:visible:has-text("Postuler")')
            if not apply_btn:
                apply_btn = page.query_selector(
                    'button:visible:has-text("Apply")')
            # 3. Fallback: first visible button on the page (avoid close/cancel if possible)
            if not apply_btn:
                btns = page.query_selector_all('button:visible')
                for btn in btns:
                    label = (btn.get_attribute("aria-label") or "").lower()
                    text = (btn.inner_text() or "").lower()
                    if "close" in label or "cancel" in label or "fermer" in label or "annuler" in label:
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
            logger.warning(
                f"No Indeed Apply button found for {job_url}")
            page.close()
            return False

        # add timeout for the wizard loop
        start_time = time.time()
        while True:
            if time.time() - start_time > 40:
                logger.warning(
                    f"Timeout applying to {job_url}, closing tab and moving to next.")
                break
            current_url = page.url
            # Resume step: select resume card if present
            resume_card = page.query_selector(
                '[data-testid="FileResumeCardHeader-title"]')
            if resume_card:
                # Click the resume card (or its parent if needed)
                try:
                    resume_card.click()
                except Exception:
                    parent = resume_card.evaluate_handle(
                        'node => node.parentElement')
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

            # try to find a submit button ( dynamic text) idk if it's working
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

            # fallback: try to find a visible and enabled button to continue (other stesp)
            btn = page.query_selector(
                'button[type="button"]:not([aria-disabled="true"]), button[type="submit"]:not([aria-disabled="true"])')
            if btn:
                click_and_wait(btn, 3)
                if "confirmation" in page.url or "submitted" in page.url:
                    logger.info(f"Applied successfully to {job_url}")
                    break
            else:
                logger.warning(
                    f"No continue/submit button found at {current_url}")
                break
        page.close()
        return True
    except Exception as e:
        logger.error(f"Error applying to {job_url}: {e}")
        page.close()
        return False


def setup_logger():
    logger = logging.getLogger("indeed_apply")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("indeed_apply.log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


with Camoufox(user_data_dir=user_data_dir,
              persistent_context=True) as browser:
    logger = setup_logger()
    page = browser.new_page()
    base_domain = domain_for_language(language)
    page.goto("https://" + base_domain)

    cookies = page.context.cookies()
    ppid_cookie = next(
        (cookie for cookie in cookies if cookie['name'] == 'PPID'), None)
    if not ppid_cookie:
        print("Token not found, please log in to Indeed first.")
        print("Redirecting to login page...")
        print("You need  to restart the bot after logging in.")
        # Ensure 'hl' is a valid code; default to 'en' for English locales
        hl = "en" if str(language).lower() in ("en", "us", "uk") else str(language).lower()
        page.goto(
            "https://secure.indeed.com/auth?hl=" + hl)
        time.sleep(1000)  # wait for manual login
    else:
        print("Token found, proceeding with job search...")
        search_config = config.get("search", {})
        base_url = search_config.get("base_url", "")
        start = search_config.get("start", "")
        end = search_config.get("end", "")

        listURL = []
        i = start
        while i <= end:
            url = f"{base_url}&start={i}"
            listURL.append(url)
            i += 10

        all_job_links = []
        for url in listURL:
            print(f"Visiting URL: {url}")
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            print(
                "Waiting for page to load, if any cloudflare protection button appears... please click it.")
            time.sleep(10)

            try:
                links = collect_indeed_apply_links(page, language)
                all_job_links.extend(links)
                print(f"Found {len(links)} Indeed Apply jobs on this page.")
            except Exception as e:
                print("Error extracting jobs:", e)
            time.sleep(5)

        print(f"Total Indeed Apply jobs found: {len(all_job_links)}")
        for job_url in all_job_links:
            print(f"Applying to: {job_url}")
            success = apply_to_job(browser, job_url, language, logger)
            if not success:
                logger.error(f"Failed to apply to {job_url}")
            time.sleep(5)
        all_job_links = []
        for url in listURL:
            print(f"Visiting URL: {url}")
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(7)
            try:
                links = collect_indeed_apply_links(page, language)
                all_job_links.extend(links)
                print(f"Found {len(links)} Indeed Apply jobs on this page.")
            except Exception as e:
                print("Error extracting jobs:", e)
            time.sleep(5)

        print(f"Total Indeed Apply jobs found: {len(all_job_links)}")
        for job_url in all_job_links:
            print(f"Applying to: {job_url}")
            success = apply_to_job(browser, job_url, language, logger)
            if not success:
                logger.error(f"Failed to apply to {job_url}")
            time.sleep(5)
