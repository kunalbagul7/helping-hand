# ==============================================================
# auto_apply.py  —  STEP 3
# Reads jobs_url.csv (external apply URLs from Step 2),
# visits each URL, detects Google Form or normal website form,
# fills & submits the form automatically.
# Skips already-applied jobs using applied.txt log.
# ==============================================================

from playwright.sync_api import sync_playwright
from config import (
    JOBS_URL_CSV, RESUME_PATH, APPLIED_LOG,
    PROFILE, KEYWORD_ANSWERS,
    DELAY_MIN, DELAY_MAX
)
import pandas as pd
import random
import time
import re
import os
from database import get_pending_jobs
from database import update_status
from database import save_application_history


jobs = get_pending_jobs()

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def human_delay(min_s=None, max_s=None):
    lo = min_s if min_s is not None else DELAY_MIN
    hi = max_s if max_s is not None else DELAY_MAX
    time.sleep(random.uniform(lo, hi))


def load_applied_log():
    """Return set of URLs already applied to."""
    if os.path.exists(APPLIED_LOG):
        with open(APPLIED_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def mark_applied(url):
    """Append URL to the applied log so we never apply twice."""
    os.makedirs(os.path.dirname(APPLIED_LOG), exist_ok=True)
    with open(APPLIED_LOG, "a", encoding="utf-8") as f:
        f.write(url.strip() + "\n")


def pick_answer_for(text):
    """
    Match a field's label/placeholder/name text against KEYWORD_ANSWERS.
    Returns the best matching answer string, or None.
    """
    text = text.lower().strip()
    for keyword, answer in KEYWORD_ANSWERS.items():
        if keyword in text:
            return str(answer)
    return None


# ------------------------------------------------------------------
# GOOGLE FORM DETECTION
# ------------------------------------------------------------------

def get_google_form_url(page):
    """Try to find an embedded Google Form URL on the current page."""
    human_delay(4, 6)

    # Check iframe URLs
    for frame in page.frames:
        if "docs.google.com/forms" in frame.url:
            return frame.url

    # Check meta embedURL tag
    try:
        meta = page.locator('meta[itemprop="embedURL"]')
        if meta.count() > 0:
            val = meta.first.get_attribute("content") or ""
            if "docs.google.com/forms" in val:
                return val
    except Exception:
        pass

    # Search raw HTML
    try:
        html = page.content()
        match = re.search(
            r'https://docs\.google\.com/forms/[^\s"\'<>]+',
            html
        )
        if match:
            return match.group(0)
    except Exception:
        pass

    return None


# ------------------------------------------------------------------
# FILL GOOGLE FORM
# ------------------------------------------------------------------

def fill_google_form(page):
    """Fill every question in a Google Form and submit."""
    human_delay(2, 4)

    questions = page.locator('div[role="listitem"]')
    total = questions.count()
    print(f"  Found {total} Google Form questions")

    for i in range(total):
        try:
            q    = questions.nth(i)
            text = q.inner_text().lower()
            print(f"  Q{i}: {text[:80]}")

            # ── Text inputs ────────────────────────────────────────
            inputs = q.locator(
                'input[type="text"], input[type="email"], input[type="tel"]'
            )

            if inputs.count() > 0:
                answer = pick_answer_for(text)
                if answer:
                    inputs.first.fill(answer)
                    print(f"    → filled: {answer[:60]}")

            # ── Textarea ───────────────────────────────────────────
            textarea = q.locator("textarea")
            if textarea.count() > 0:
                answer = pick_answer_for(text)
                if answer:
                    textarea.first.fill(answer)
                    print(f"    → filled textarea: {answer[:60]}")

            # ── Dropdown (listbox) ─────────────────────────────────
            if "job position" in text or "position" in text or "role" in text:
                try:
                    dropdown = q.locator('[role="listbox"]').first
                    if dropdown.count() > 0:
                        dropdown.click()
                        page.wait_for_timeout(800)

                    option = page.get_by_text(PROFILE["job_position"], exact=True)
                    if option.count() > 0:
                        option.first.click()
                        print(f"    → selected: {PROFILE['job_position']}")
                except Exception as e:
                    print(f"    Dropdown error: {e}")

            # ── Yes/No radio buttons ───────────────────────────────
            confirm_keywords = [
                "email address is correct",
                "primary/junk",
                "recruiter email",
                "confirm",
                "agree",
            ]
            if any(kw in text for kw in confirm_keywords):
                radios = q.locator('[role="radio"]')
                if radios.count() > 0:
                    radios.first.click()
                    print("    → clicked Yes radio")

        except Exception as e:
            print(f"  Question {i} error: {e}")

    # ── File upload ────────────────────────────────────────────────
    try:
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0 and os.path.exists(RESUME_PATH):
            file_input.first.set_input_files(RESUME_PATH)
            print(f"  Uploaded resume → {RESUME_PATH}")
    except Exception as e:
        print(f"  File upload error: {e}")

    # ── Submit ─────────────────────────────────────────────────────
    try:
        submit_btn = page.get_by_role(
            "button", name=re.compile("submit", re.I)
        )
        if submit_btn.count() > 0:
            submit_btn.first.click()
            print("  Google Form submitted!")
            return True
        else:
            # Multi-page form — click Next
            next_btn = page.get_by_role(
                "button", name=re.compile("next", re.I)
            )
            if next_btn.count() > 0:
                next_btn.first.click()
                print("  Clicked Next (multi-page form)")
    except Exception as e:
        print(f"  Submit error: {e}")

    return False


# ------------------------------------------------------------------
# CLICK APPLY BUTTON ON EXTERNAL SITE
# ------------------------------------------------------------------

def click_apply_button(page):
    """Try to click an Apply button on a company careers page."""
    apply_keywords = [
        "Apply Now", "Apply Here", "Apply",
        "Start Application", "Submit Application",
        "Register", "Join Now", "Careers", "Career",
    ]

    for text in apply_keywords:
        try:
            btn = page.get_by_text(text, exact=False)
            if btn.count() > 0:
                btn.first.click()
                print(f"  Clicked button: {text}")
                human_delay(3, 5)
                return True
        except Exception:
            pass

    # Fallback: scan all links
    try:
        links = page.locator("a")
        for i in range(links.count()):
            try:
                link = links.nth(i)
                txt  = link.inner_text().strip().lower()
                if any(kw in txt for kw in ["apply", "career", "job"]):
                    print(f"  Clicked link: {txt}")
                    link.click()
                    human_delay(3, 5)
                    return True
            except Exception:
                pass
    except Exception:
        pass

    return False


# ------------------------------------------------------------------
# FILL NORMAL WEBSITE FORM
# ------------------------------------------------------------------

def fill_normal_form(page):
    """Fill input fields on a standard company application form."""
    print("  Filling normal website form...")

    inputs = page.locator("input")
    total  = inputs.count()
    print(f"  Found {total} input fields")

    for i in range(total):
        try:
            field       = inputs.nth(i)
            field_type  = (field.get_attribute("type") or "").lower()

            # Skip hidden / submit / checkbox / radio / file — handled separately
            if field_type in ("hidden", "submit", "button", "file"):
                continue
            if not field.is_visible():
                continue

            name        = (field.get_attribute("name")        or "").lower()
            placeholder = (field.get_attribute("placeholder") or "").lower()
            label_text  = (field.get_attribute("aria-label")  or "").lower()
            combined    = " ".join([name, placeholder, label_text])

            answer = pick_answer_for(combined)
            if answer:
                field.fill(answer)
                print(f"  Filled [{combined.strip()[:50]}] → {answer[:50]}")

        except Exception:
            pass

    # ── Textarea ───────────────────────────────────────────────────
    textareas = page.locator("textarea")
    for i in range(textareas.count()):
        try:
            ta          = textareas.nth(i)
            name        = (ta.get_attribute("name")        or "").lower()
            placeholder = (ta.get_attribute("placeholder") or "").lower()
            label_text  = (ta.get_attribute("aria-label")  or "").lower()
            combined    = " ".join([name, placeholder, label_text])

            answer = pick_answer_for(combined)
            if answer:
                ta.fill(answer)
                print(f"  Filled textarea [{combined.strip()[:50]}] → {answer[:50]}")
        except Exception:
            pass

    # ── Resume upload ──────────────────────────────────────────────
    try:
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0 and os.path.exists(RESUME_PATH):
            file_input.first.set_input_files(RESUME_PATH)
            print(f"  Uploaded resume → {RESUME_PATH}")
    except Exception as e:
        print(f"  File upload error: {e}")

    print("  Normal form filled.")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------


already_done = load_applied_log()
update_status(
    job_id,
    "Applied"
)


total = len(jobs)
print(f"\nTOTAL JOBS TO APPLY: {total}")
print(f"Already applied (from log): {len(already_done)}")

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    for index, row in jobs.iterrows():

        title      = str(row.get("title", "Unknown"))
        apply_url  = str(row.get("apply_url", ""))
        form_type  = str(row.get("form_type", ""))

        print(f"\n{'='*60}")
        print(f"[{index + 1}/{total}] {title}")
        print(f"  URL      : {apply_url}")
        print(f"  Form Type: {form_type}")

        # ── Skip empty / Easy Apply (already handled in Step 2) ───
        if not apply_url or apply_url.strip() in ("", "nan", "linkedin_easy_apply"):
            print("  Skipping — no external URL or already applied via Easy Apply.")
            continue

        # ── Skip already applied ───────────────────────────────────
        if apply_url in already_done:
            print("  Already applied — skipping.")
            continue

        page = browser.new_page()

        try:
            page.goto(
                apply_url,
                wait_until="domcontentloaded",
                timeout=120000
            )
            human_delay(2, 4)

        except Exception as e:
            print(f"  Cannot open URL: {e}")
            page.close()
            continue

        # ── Google Form ────────────────────────────────────────────
        google_form_url = get_google_form_url(page)

        if google_form_url:
            print(f"  Google Form detected: {google_form_url}")
            form_page = browser.new_page()

            try:
                form_page.goto(
                    google_form_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                fill_google_form(form_page)

                # Wait for user to verify before marking done
                input("\n  >>> Press ENTER after confirming submission...")
                mark_applied(apply_url)
                print(f"  Logged as applied: {apply_url}")

            except Exception as e:
                print(f"  Google Form error: {e}")
            finally:
                form_page.close()

        # ── Normal Website Form ────────────────────────────────────
        else:
            print("  Normal website form")

            # Try to find and click an Apply button first
            click_apply_button(page)

            # Re-check for Google Form after clicking Apply
            google_form_url = get_google_form_url(page)
            if google_form_url:
                print(f"  Google Form found after clicking Apply: {google_form_url}")
                form_page = browser.new_page()
                try:
                    form_page.goto(google_form_url, wait_until="domcontentloaded", timeout=60000)
                    fill_google_form(form_page)
                    input("\n  >>> Press ENTER after confirming submission...")
                    mark_applied(apply_url)
                except Exception as e:
                    print(f"  Google Form error: {e}")
                finally:
                    form_page.close()
            else:
                fill_normal_form(page)
                input("\n  >>> Press ENTER after confirming submission...")
                mark_applied(apply_url)
                print(f"  Logged as applied: {apply_url}")

        page.close()
        human_delay()

    browser.close()

print(f"\n{'='*60}")
print("ALL JOBS PROCESSED")
print(f"{'='*60}")