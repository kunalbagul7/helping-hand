from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import os
import time

# ==========================
# FILE PATHS
# ==========================

SESSION_FILE  = r"/create_session/linkedin_session.json"
INPUT_CSV     = r"C:\Users\Kunal\PycharmProjects\jobs_applyer\data\jobs.csv"
OUTPUT_CSV    = r"C:\Users\Kunal\PycharmProjects\jobs_applyer\data\jobs_url.csv"
RESUME_PATH = r"C:\Users\DHIRAJ MORE\Downloads\Dhiraj_More_9767967412.pdf"

# ==========================
# YOUR PROFILE INFO
# Fill these in once — used to answer Easy Apply form fields
# ==========================

PROFILE = {
    "first_name":       "Dhiraj",
    "last_name":        "More",
    "email":            "moredhiraj5234@gmail.com",       # change
    "phone":            "9767967412",
    "phone_country":    "India (+91)",
    "city":             "Pune",
    "state":            "Maharashtra",
    "country":          "India",
    "linkedin_url":     "www.linkedin.com/in/dhiraj-more-188881257",   # change
    "github_url":       "https://github.com/dhiraj",            # change
    "years_experience": "1",
    "current_ctc":      "0",
    "expected_ctc":     "400000",
    "notice_period":    "0",                # in days
    "willing_relocate": "Yes",
    "work_auth":        "Yes",              # authorized to work in India
    "gender":           "Male",
    "cover_letter": (
        "I am a final-year Computer Engineering student at Godavari College of Engineering, "
        "Jalgaon, graduating in August 2026. I have hands-on experience in SQL Server, Python, "
        "Power BI, and data analysis. I am eager to contribute and grow as a Data Analyst / SQL Developer."
    ),
}

# ==========================
# KEYWORD → ANSWER MAP
# Maps label keywords to PROFILE values.
# Add more entries as you encounter new fields.
# ==========================

KEYWORD_ANSWERS = {
    "first name":          PROFILE["first_name"],
    "last name":           PROFILE["last_name"],
    "full name":           f"{PROFILE['first_name']} {PROFILE['last_name']}",
    "email":               PROFILE["email"],
    "phone":               PROFILE["phone"],
    "mobile":              PROFILE["phone"],
    "city":                PROFILE["city"],
    "location":            PROFILE["city"],
    "state":               PROFILE["state"],
    "country":             PROFILE["country"],
    "linkedin":            PROFILE["linkedin_url"],
    "github":              PROFILE["github_url"],
    "website":             PROFILE["github_url"],
    "portfolio":           PROFILE["github_url"],
    "years of experience": PROFILE["years_experience"],
    "experience":          PROFILE["years_experience"],
    "current ctc":         PROFILE["current_ctc"],
    "current salary":      PROFILE["current_ctc"],
    "expected ctc":        PROFILE["expected_ctc"],
    "expected salary":     PROFILE["expected_ctc"],
    "notice period":       PROFILE["notice_period"],
    "salary":              PROFILE["expected_ctc"],
    "cover letter":        PROFILE["cover_letter"],
    "message":             PROFILE["cover_letter"],
    "summary":             PROFILE["cover_letter"],
    "relocate":            PROFILE["willing_relocate"],
    "relocation":          PROFILE["willing_relocate"],
    "authorized":          PROFILE["work_auth"],
    "sponsorship":         "No",
    "gender":              PROFILE["gender"],
    "veteran":             "I am not a veteran",
    "disability":          "No",
    "notice":              PROFILE["notice_period"],
    "zipcode":             "425001",
    "zip":                 "425001",
    "pincode":             "425001",
}


# ==========================
# CLICK APPLY BUTTON
# ==========================

def click_apply_button(page):
    selectors = [
        'button:has-text("Easy Apply")',
        'button:has-text("Apply")',
        'button:has-text("Continue applying")',
        '[aria-label*="Easy Apply"]',
        '[aria-label*="Apply"]',
        'a:has-text("Apply")',
        'a:has-text("Apply Now")',
    ]

    for selector in selectors:
        try:
            button = page.locator(selector).first
            if button.count() > 0:
                button.scroll_into_view_if_needed()
                button.click(force=True)
                print(f"  Clicked: {selector}")
                return True
        except:
            pass

    return False


# ==========================
# DETECT FORM TYPE
# ==========================

def get_form_type(url):
    if not url:
        return "not_found"

    url = url.lower()

    if "docs.google.com/forms" in url:
        return "google_form"
    elif "greenhouse" in url:
        return "greenhouse"
    elif "lever.co" in url:
        return "lever"
    elif "workday" in url:
        return "workday"
    elif "linkedin.com" in url:
        return "easy_apply"
    else:
        return "other"


# ==========================
# HELPER: GET LABEL FOR A FIELD
# ==========================

def get_field_label(field):
    """Try to find the label text associated with an input/select/textarea."""
    try:
        # Method 1: aria-label attribute
        aria = field.get_attribute("aria-label") or ""
        if aria.strip():
            return aria.strip().lower()

        # Method 2: id → <label for="id">
        field_id = field.get_attribute("id") or ""
        if field_id:
            page = field.page
            label = page.locator(f'label[for="{field_id}"]')
            if label.count() > 0:
                return (label.first.inner_text() or "").strip().lower()

        # Method 3: placeholder
        placeholder = field.get_attribute("placeholder") or ""
        if placeholder.strip():
            return placeholder.strip().lower()

        # Method 4: nearest ancestor label text
        label_text = field.evaluate(
            """el => {
                let node = el;
                for (let i = 0; i < 5; i++) {
                    node = node.parentElement;
                    if (!node) break;
                    const label = node.querySelector('label, span, legend');
                    if (label && label.innerText.trim()) return label.innerText.trim().toLowerCase();
                }
                return "";
            }"""
        )
        return label_text or ""

    except:
        return ""


# ==========================
# HELPER: PICK BEST ANSWER
# ==========================

def pick_answer(label):
    """Match a field label to a KEYWORD_ANSWERS entry."""
    label = label.lower()
    for keyword, answer in KEYWORD_ANSWERS.items():
        if keyword in label:
            return answer
    return None


# ==========================
# FILL ALL VISIBLE FIELDS ON CURRENT STEP
# ==========================

def fill_form_fields(page):
    """
    Fills text inputs, textareas, selects, radios, checkboxes, and
    uploads resume on the currently visible Easy Apply dialog step.
    """
    dialog = page.locator('div[role="dialog"]')

    # ── Text inputs & textareas ──────────────────────────────────────────
    text_fields = dialog.locator(
        'input[type="text"], input[type="email"], input[type="tel"], input[type="number"], input:not([type]), textarea')
    count = text_fields.count()

    for i in range(count):
        field = text_fields.nth(i)
        try:
            if not field.is_visible():
                continue
            if field.is_disabled():
                continue

            # Skip file inputs — handled separately
            field_type = field.get_attribute("type") or ""
            if field_type == "file":
                continue

            current_val = field.input_value() or ""
            if current_val.strip():
                continue  # already filled (e.g. pre-populated LinkedIn data)

            label = get_field_label(field)
            answer = pick_answer(label)

            if answer:
                field.scroll_into_view_if_needed()
                field.click()
                field.fill(str(answer))
                print(f"  Filled [{label}] → {str(answer)[:60]}")
            else:
                print(f"  SKIPPED (no match) → label='{label}'")

        except Exception as e:
            print(f"  Text field error: {e}")

    # ── <select> dropdowns ───────────────────────────────────────────────
    selects = dialog.locator("select")
    for i in range(selects.count()):
        sel = selects.nth(i)
        try:
            if not sel.is_visible():
                continue

            label = get_field_label(sel)
            answer = pick_answer(label)

            if answer:
                # Try exact match first, then partial
                options = sel.locator("option").all_inner_texts()
                matched = next(
                    (o for o in options if answer.lower() in o.lower()),
                    None
                )
                if matched:
                    sel.select_option(label=matched)
                    print(f"  Selected [{label}] → {matched}")
                else:
                    print(f"  No option match for [{label}] answer='{answer}'")
            else:
                print(f"  SKIPPED select (no match) → label='{label}'")

        except Exception as e:
            print(f"  Select error: {e}")

    # ── Radio buttons ────────────────────────────────────────────────────
    # LinkedIn renders them as <input type="radio"> inside a fieldset with a <legend>
    fieldsets = dialog.locator("fieldset")
    for i in range(fieldsets.count()):
        fs = fieldsets.nth(i)
        try:
            legend = fs.locator("legend").first
            legend_text = (legend.inner_text() or "").strip().lower()
            answer = pick_answer(legend_text)

            if not answer:
                continue

            radios = fs.locator('input[type="radio"]')
            for j in range(radios.count()):
                radio = radios.nth(j)
                radio_label_el = fs.locator(f'label[for="{radio.get_attribute("id")}"]')
                radio_label = (radio_label_el.inner_text() or "").strip().lower() if radio_label_el.count() > 0 else ""

                if answer.lower() in radio_label:
                    radio.check()
                    print(f"  Radio [{legend_text}] → {radio_label}")
                    break

        except Exception as e:
            print(f"  Radio error: {e}")

    # ── Checkboxes ───────────────────────────────────────────────────────
    checkboxes = dialog.locator('input[type="checkbox"]')
    for i in range(checkboxes.count()):
        cb = checkboxes.nth(i)
        try:
            if not cb.is_visible():
                continue

            label = get_field_label(cb)

            # Only check "I agree / I certify / I confirm" checkboxes
            if any(kw in label for kw in ["agree", "certif", "confirm", "acknowledge", "consent"]):
                if not cb.is_checked():
                    cb.check()
                    print(f"  Checked [{label}]")

        except Exception as e:
            print(f"  Checkbox error: {e}")

    # ── File upload (resume) ─────────────────────────────────────────────
    file_inputs = dialog.locator('input[type="file"]')
    for i in range(file_inputs.count()):
        fi = file_inputs.nth(i)
        try:
            if os.path.exists(RESUME_PATH):
                fi.set_input_files(RESUME_PATH)
                print(f"  Uploaded resume → {RESUME_PATH}")
            else:
                print(f"  Resume not found at {RESUME_PATH} — skipping upload")
        except Exception as e:
            print(f"  File upload error: {e}")

    # Small pause to let LinkedIn validate fields
    page.wait_for_timeout(1000)


# ==========================
# COMPLETE EASY APPLY  (MAIN LOOP)
# ==========================

def complete_easy_apply(page):
    """
    Iterates through all Easy Apply steps:
      1. Fill fields on current step
      2. Click Next / Review
      3. On final step click Submit
      4. Click Done to dismiss
    """
    MAX_STEPS = 15  # safety limit
    step = 0

    while step < MAX_STEPS:
        page.wait_for_timeout(2000)
        step += 1
        print(f"\n  --- Easy Apply step {step} ---")

        # Fill everything visible on this step
        try:
            fill_form_fields(page)
        except Exception as e:
            print(f"  fill_form_fields error: {e}")

        page.wait_for_timeout(1000)

        # ── Submit ───────────────────────────────────────────────────────
        submit_btn = page.locator('button:has-text("Submit application")')
        if submit_btn.count() > 0 and submit_btn.first.is_visible():
            print("  Clicking Submit")
            submit_btn.first.click()
            page.wait_for_timeout(4000)

            # Dismiss confirmation dialog
            done_btn = page.locator('button:has-text("Done")')
            if done_btn.count() > 0 and done_btn.first.is_visible():
                done_btn.first.click()
                print("  Clicked Done — Application submitted!")
            return True

        # ── Review ───────────────────────────────────────────────────────
        review_btn = page.locator('button:has-text("Review")')
        if review_btn.count() > 0 and review_btn.first.is_visible():
            print("  Clicking Review")
            review_btn.first.click()
            try:
                review_btn.first.wait_for(state="hidden", timeout=5000)
            except:
                pass
            page.wait_for_timeout(1500)
            continue

        # ── Next ─────────────────────────────────────────────────────────
        next_btn = page.locator('button:has-text("Next")')
        if next_btn.count() > 0 and next_btn.first.is_visible():
            print("  Clicking Next")
            next_btn.first.click()
            try:
                next_btn.first.wait_for(state="hidden", timeout=5000)
            except:
                pass
            page.wait_for_timeout(1500)
            continue

        # ── Done (already submitted or error page) ────────────────────────
        done_btn = page.locator('button:has-text("Done")')
        if done_btn.count() > 0 and done_btn.first.is_visible():
            done_btn.first.click()
            print("  Clicked Done")
            return True

        # No recognized button — bail out
        print("  No Next/Review/Submit button found — stopping.")
        break

    print("  Easy Apply loop ended.")
    return False


# ==========================
# MAIN
# ==========================

jobs = pd.read_csv(INPUT_CSV)
saved_urls = set()

try:
    old = pd.read_csv(OUTPUT_CSV)
    saved_urls = set(old["apply_url"].dropna().tolist())
except:
    pass

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )

    context = browser.new_context(
        storage_state=SESSION_FILE
    )

    page = context.new_page()
    total = len(jobs)
    print(f"\nTOTAL JOBS: {total}")

    for index, row in jobs.iterrows():

        title = str(row["title"])
        linkedin_url = str(row["url"])

        print(f"\n[{index + 1}/{total}] {title}")

        apply_url = ""

        try:
            page.goto(
                linkedin_url,
                wait_until="domcontentloaded",
                timeout=120000
            )
            page.wait_for_timeout(5000)

            old_pages = len(context.pages)
            success = click_apply_button(page)

            if success:

                # ── STEP 1: Wait up to 8s for Easy Apply dialog ──────────
                dialog_appeared = False
                try:
                    page.wait_for_selector(
                        'div[role="dialog"]',
                        timeout=8000,
                        state="visible"
                    )
                    dialog_appeared = True
                    print("  Dialog detected — Easy Apply")
                except:
                    pass  # no dialog — may be new tab or page redirect

                # ── STEP 2: Handle Easy Apply dialog ─────────────────────
                if dialog_appeared:
                    popup = page.locator('div[role="dialog"]')
                    if popup.count() > 0 and popup.first.is_visible():
                        print("  Easy Apply popup detected — filling form...")
                        submitted = complete_easy_apply(page)
                        apply_url = "linkedin_easy_apply"
                        if submitted:
                            print("  ✓ Application submitted successfully")
                        else:
                            print("  ✗ Application may be incomplete")
                        # Skip new-tab / redirect checks — dialog handled it
                        pass

                # ── STEP 3: No dialog — check for new tab or redirect ────
                else:
                    page.wait_for_timeout(3000)

                    # New tab opened (external apply site)
                    if len(context.pages) > old_pages:
                        new_page = context.pages[-1]
                        try:
                            new_page.wait_for_load_state(
                                "domcontentloaded", timeout=30000
                            )
                        except:
                            pass

                        apply_url = new_page.url
                        print(f"  New Tab URL: {apply_url}")

                        if new_page != page:
                            new_page.close()

                    else:
                        # Same-tab redirect (e.g. page.url changed)
                        apply_url = page.url
                        print(f"  Redirect URL: {apply_url}")

                        # LinkedIn sometimes redirects to its own /apply/ URL
                        # instead of opening a dialog — navigate there and wait
                        if "linkedin.com" in apply_url and "/apply" in apply_url:
                            print("  LinkedIn apply redirect — waiting for dialog...")
                            try:
                                page.goto(
                                    apply_url,
                                    wait_until="domcontentloaded",
                                    timeout=30000
                                )
                                page.wait_for_selector(
                                    'div[role="dialog"]',
                                    timeout=8000,
                                    state="visible"
                                )
                                popup = page.locator('div[role="dialog"]')
                                if popup.count() > 0 and popup.first.is_visible():
                                    print("  Dialog opened on apply page — filling...")
                                    submitted = complete_easy_apply(page)
                                    apply_url = "linkedin_easy_apply"
                                    if submitted:
                                        print("  ✓ Application submitted successfully")
                                    else:
                                        print("  ✗ Application may be incomplete")
                            except Exception as e:
                                print(f"  LinkedIn apply page error: {e}")

            else:
                print("  No Apply button found.")
                apply_url = ""

        except Exception as e:
            print(f"  Failed: {e}")

        form_type = get_form_type(apply_url)
        print(f"  Apply URL : {apply_url}")
        print(f"  Form Type : {form_type}")

        if apply_url:
            exists = apply_url in saved_urls
            saved_urls.add(apply_url)

            if not exists:
                results.append({
                    "title": title,
                    "linkedin_url": linkedin_url,
                    "apply_url": apply_url,
                    "form_type": form_type,
                })
                pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
                print(f"  Saved: {apply_url}")
            else:
                print(f"  Duplicate skipped: {apply_url}")

        # Always save after each job
        pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)

    browser.close()

# ==========================
# FINAL SAVE & CLEANUP
# ==========================

df = pd.DataFrame(results)
df.drop_duplicates(subset=["apply_url"], inplace=True)
df = df[df["apply_url"] != ""]
df = df[df["apply_url"] != "linkedin_easy_apply"]
df.to_csv(OUTPUT_CSV, index=False)

print("\nSaved Successfully!")
print(OUTPUT_CSV)