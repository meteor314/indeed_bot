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
                        job_url = f"https://{language}.indeed.com{job_url}"
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
                
                # Cleaned up if statment for translations
                applyText = ["déposer ma candidature", "soumettre", "submit", "apply", "bewerben", "postular"]  # add more translations if needed
                
                if (text in applyText):
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


if __name__ == "__main__":
    with Camoufox(user_data_dir=user_data_dir,
                persistent_context=True) as browser:
        logger = setup_logger()
        page = browser.new_page()
        page.goto("https://" + language + ".indeed.com")

        cookies = page.context.cookies()
        ppid_cookie = next(
            (cookie for cookie in cookies if cookie['name'] == 'PPID'), None)
        if not ppid_cookie:
            print("Token not found, please log in to Indeed first.")
            print("Redirecting to login page...")
            print("You need  to restart the bot after logging in.")
            page.goto(
                "https://secure.indeed.com/auth?hl=" + language)
            time.sleep(5)
            exit()  # requires bot restart

        else:
            print("Token found, proceeding with job search...")
            search_config = config.get("search", {})

            # simplified unpacking (please test)
            base_url, start, end = (search_config.get(k, "") for k in ("base_url", "start", "end"))

            # edge case check for missing config values 
            if not base_url or start is None or end is None:
                print("Please configure base_url, start, and end in config.yaml")
                exit(1)

            

            # simplified URL generation
            listURL = []
            for i in range(start, end + 1, 10): # step is 10 for Indeed pagination
                url = f"{base_url}&start={i}"
                listURL.append(url)

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
                    print("Error extracting job, removing url:", e)
                    listURL.remove(url)  # remove problematic URL
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
