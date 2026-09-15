from playwright.sync_api import sync_playwright

import pandas as pd
import re


# ======================
# YOUR DETAILS
# ======================

PROFILE = {
     "name" : "dhiraj",
    "first name":"Dhiraj",
    "last name":"More",
    "full name":"Dhiraj Sitaram More",
    "email": "moredhiraj5234@gmail.com",
    "phone": "9767967412",
    "whatsapp number":"9767967412",
    "linkedin": "www.linkedin.com/in/dhiraj-more-188881257",
    "location": "Pune, Maharashtra, India",
    "experience": "6 months",
    "job_position": "Python Developer"
}

RESUME_PATH = r"/data/Kunal_Bagul.pdf"
CSV_PATH = r"C:\Users\Kunal\PycharmProjects\jobs_applyer\data\jobs_url.csv"

# ======================
# FIND GOOGLE FORM
# ======================

def get_google_form_url(page):
    page.wait_for_timeout(5000)

    # Check all frames
    for frame in page.frames:
        print("FRAME:", frame.url)

        if "docs.google.com/forms" in frame.url:
            return frame.url

    # Check meta tag
    try:
        meta = page.locator(
            'meta[itemprop="embedURL"]'
        )

        if meta.count() > 0:
            return meta.first.get_attribute(
                "content"
            )
    except:
        pass

    # Search entire HTML
    try:
        html = page.content()

        match = re.search(
            r'https://docs\.google\.com/forms/[^\s"\']+',
            html
        )

        if match:
            return match.group(0)
    except:
        pass

    return None


# ======================
# FILL FORM
# ======================

def fill_google_form(page):

    page.wait_for_timeout(3000)

    questions = page.locator('div[role="listitem"]')
    total = questions.count()


    print(f"\nFound {total} questions")

    for i in range(total):

        try:
            q = questions.nth(i)
            text = q.inner_text().lower()

            print(f"\nQuestion {i}:")
            print(text)

            # =====================
            # TEXT INPUTS
            # =====================

            inputs = q.locator(
                'input[type="text"],input[type="email"],input[type="tel"]'
            )

            if inputs.count() > 0:

                field = inputs.first


                if "Enter your first name" in text:
                    field.fill(PROFILE["name"])
                    print("Filled Name")
                elif "Enter your last name" in text:
                    field.fill(PROFILE["last_name"])
                    print("last name filled")

                elif "email" in text:
                    field.fill(PROFILE["email"])
                    print("Filled Email")

                elif (
                    "phone" in text
                    or "contact" in text
                    or "mobile" in text
                ):
                    field.fill(PROFILE["phone"])
                    print("Filled Phone")

                elif "linkedin" in text:
                    field.fill(PROFILE["linkedin"])
                    print("Filled LinkedIn")

                elif "location" in text:
                    field.fill(PROFILE["location"])
                    print("Filled Location")

                elif "experience" in text:
                    field.fill(PROFILE["experience"])
                    print("Filled Experience")

            # =====================
            # JOB POSITION DROPDOWN
            # =====================

            if "job position" in text:

                try:
                    # Open dropdown
                    dropdown = q.locator('[role="listbox"]').first

                    if dropdown.count() > 0:
                        dropdown.click()
                        page.wait_for_timeout(1000)

                    # Click option
                    option = page.get_by_text(
                        PROFILE["job_position"],
                        exact=True
                    )

                    option.click()

                    print(
                        f'Selected {PROFILE["job_position"]}'
                    )

                except Exception as e:
                    print(
                        "Job Position selection failed:",
                        e
                    )
            # =====================
            # YES RADIO BUTTONS
            # =====================

            if (
                "email address is correct" in text
                or "primary/junk" in text
                or "recruiter email addresses" in text
            ):

                radios = q.locator(
                    '[role="radio"]'
                )

                if radios.count() > 0:
                    radios.first.click()
                    print("Clicked Yes")

        except Exception as e:
            print("Failed:", e)

    # =====================
    # FILE UPLOAD
    # =====================

    try:
        file_input = page.locator(
            'input[type="file"]'
        )

        if file_input.count() > 0:
            file_input.first.set_input_files(
                RESUME_PATH
            )
            print("Resume Uploaded")

    except:
        pass

    # =====================
    # SUBMIT
    # =====================

    try:

        submit = page.get_by_role(
            "button",
            name=re.compile(
                "submit",
                re.I
            )
        )

        if submit.count() > 0:
            submit.first.click()
            print("Form Submitted!")

        else:
            next_btn = page.get_by_role(
                "button",
                name=re.compile(
                    "next",
                    re.I
                )
            )

            if next_btn.count() > 0:
                next_btn.first.click()
                print("Next Clicked")

    except Exception as e:
        print(e)
# ======================
# MAIN
# ======================

# ======================
# CLICK APPLY BUTTON
# ======================

def click_apply_button(page):

    apply_keywords = [
        "Apply",
        "Apply Now",
        "Apply Here",
        "Start Application",
        "Submit Application",
        "Register",
        "Join Now",
        "Career",
        "Careers",
        "Submmit"
    ]

    # Text buttons
    for text in apply_keywords:
        try:
            btn = page.get_by_text(
                text,
                exact=False
            )

            if btn.count() > 0:
                btn.first.click()

                print(
                    f"Clicked button: {text}"
                )

                page.wait_for_timeout(5000)

                return True

        except:
            pass

    # Links
    try:
        links = page.locator("a")

        for i in range(links.count()):

            try:
                link = links.nth(i)

                txt = (
                    link.inner_text()
                    .strip()
                    .lower()
                )

                if (
                    "apply" in txt
                    or "career" in txt
                    or "job" in txt
                ):

                    print(
                        "Clicked link:",
                        txt
                    )

                    link.click()

                    page.wait_for_timeout(
                        5000
                    )

                    return True

            except:
                pass

    except:
        pass

    return False


# ======================
# FILL NORMAL WEBSITE FORMS
# ======================

def fill_normal_form(page):

    print(
        "\nTrying to fill normal website form..."
    )

    inputs = page.locator(
        "input"
    )

    total = inputs.count()

    print(
        f"Found {total} input fields"
    )

    for i in range(total):

        try:

            field = inputs.nth(i)

            name = (
                field.get_attribute(
                    "name"
                )
                or ""
            ).lower()

            placeholder = (
                field.get_attribute(
                    "placeholder"
                )
                or ""
            ).lower()

            text = (
                name
                + " "
                + placeholder
            )
            print(text)
            if (""
                "name") in text:
                field.fill(
                    PROFILE["name"]
                )

            elif "last_name" in text:
                field.fill(PROFILE["first_name"])

            elif "full name" in text:
                field.fill(
                    PROFILE["full name"]
                           )
            elif "Enter your last name" in text:
                field.fill(PROFILE["last name"])

            elif "email" in text:
                field.fill(
                    PROFILE["email"]
                )

            elif (
                "phone" in text
                or "mobile" in text or "whatsapp" in text
            ):
                field.fill(
                    PROFILE["phone"]
                )

            elif "linkedin" in text:
                field.fill(
                    PROFILE["linkedin"]
                )

            elif "location" in text:
                field.fill(
                    PROFILE["location"]
                )

            elif (
                "experience" in text
            ):
                field.fill(
                    PROFILE["experience"]
                )

        except:
            pass

    # Resume Upload

    try:
        file_input = page.locator(
            'input[type="file"]'
        )

        if file_input.count() > 0:

            file_input.first.set_input_files(
                RESUME_PATH
            )

            print(
                "Resume uploaded"
            )

    except:
        pass

    print(
        "Normal form filled."
    )


# ======================
# MAIN
# ======================

jobs = pd.read_csv(CSV_PATH)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    for index, row in jobs.iterrows():

        title = str(row["title"])
        apply_url = str(row["apply_url"])
        form_type = str(row["form_type"])

        print(
            f"\n[{index+1}/{len(jobs)}]"
        )

        print(
            "Job:",
            title
        )

        print(
            "URL:",
            apply_url
        )

        if (
            apply_url == ""
            or apply_url == "nan"
        ):
            print(
                "No apply url found."
            )
            continue

        page = browser.new_page()

        try:

            page.goto(
                apply_url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(
                3000
            )

        except Exception as e:

            print(
                "Cannot open url:"
            )

            print(e)

            page.close()

            continue

        # ------------------
        # GOOGLE FORM
        # ------------------

        google_form_url = (
            get_google_form_url(
                page
            )
        )

        if google_form_url:

            print(
                "Google Form Found"
            )

            form_page = (
                browser.new_page()
            )

            form_page.goto(
                google_form_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            fill_google_form(
                form_page
            )

            input(
                "\nPress ENTER after clicking Submit..."
            )

            form_page.close()

            page.close()

            continue

        # ------------------
        # NORMAL WEBSITE
        # ------------------

        print(
            "Normal Website Form"
        )

        fill_normal_form(
            page
        )

        input(
            "\nPress ENTER after clicking Submit..."
        )

        page.close()

    browser.close()

print(
    "\nALL JOBS COMPLETED"
)