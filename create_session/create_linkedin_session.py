from playwright.sync_api import sync_playwright

SESSION_FILE = "linkedin_session.json"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="chrome"  # Uses installed Google Chrome
    )

    context = browser.new_context()
    page = context.new_page()

    print("Opening LinkedIn...")
    page.goto("https://www.linkedin.com/login")

    print("\n==========================================")
    print("1. Log in to LinkedIn manually.")
    print("2. Complete CAPTCHA if prompted.")
    print("3. Wait until your LinkedIn home page loads.")
    print("4. Press ENTER here to save the session.")
    print("==========================================\n")

    input("Press ENTER after logging in...")

    # Save cookies and local storage
    context.storage_state(path=SESSION_FILE)

    print(f"\n Session saved as: {SESSION_FILE}")

    browser.close()