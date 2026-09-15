from playwright.sync_api import sync_playwright
from scraper.job_roles import JOB_ROLES
import pandas as pd

all_jobs = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state=r"C:\Users\Kunal\PycharmProjects\jobs_applyer\create_session\linkedin_session.json"
    )

    page = context.new_page()

    for role in JOB_ROLES:

        print(f"\nSearching for: {role}")

        search_url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={role.replace(' ', '%20')}"
        )

        page.goto(
            search_url,
            timeout=60000
        )

        page.wait_for_timeout(5000)

        job_cards = page.locator("a").all()

        for card in job_cards:

            try:

                text = card.inner_text().strip()

                href = card.get_attribute("href")

                if href and href.startswith("/jobs/view/"):
                    href = "https://www.linkedin.com" + href

                if (
                    href
                    and "/jobs/view/" in href
                    and text != ""
                ):

                    print(text)

                    all_jobs.append({
                        "role": role,
                        "title": text.split("\n")[0],
                        "url": href
                    })

            except Exception:
                pass

    browser.close()

# ---------------------------------
# SAVE RESULTS TO CSV
# ---------------------------------

df = pd.DataFrame(all_jobs)

df.drop_duplicates(inplace=True)

csv_path = r"/data/jobs.csv"

df.to_csv(
    csv_path,
    index=False
)

print("\nTOTAL JOBS FOUND:")
print(len(df))

print("\nJobs saved successfully!")

print(f"\nSaved file location:\n{csv_path}")