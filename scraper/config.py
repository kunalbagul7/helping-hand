# ==============================================================
# config.py  —  Single source of truth for the entire project
# Edit your details here. All other scripts import from here.
# ==============================================================

import os

# ------------------------------------------------------------------
# FILE PATHS  (change these to match your machine)
# ------------------------------------------------------------------

BASE_DIR        = r"/data"

SESSION_FILE    = os.path.join(BASE_DIR, "linkedin_session.json")
JOBS_CSV        = os.path.join(BASE_DIR, "jobs.csv")
JOBS_URL_CSV    = os.path.join(BASE_DIR, "jobs_url.csv")
APPLIED_LOG     = os.path.join(BASE_DIR, "applied.txt")       # tracks applied URLs

RESUME_PATH     = r"/data/Kunal_Bagul.pdf"

# ------------------------------------------------------------------
# YOUR PROFILE  (one dict, used by all 3 scripts)
# ------------------------------------------------------------------
MAX_PAGES = 2
PROFILE = {
    # Name
    "first_name":       "Dhiraj",
    "last_name":        "More",
    "full_name":        "Dhiraj Sitaram More",

    # Contact
    "email":            "moredhiraj5234@gmail.com",
    "phone":            "9767967412",
    "whatsapp":         "9767967412",
    "phone_country":    "India (+91)",

    # Location
    "city":             "Pune",
    "state":            "Maharashtra",
    "country":          "India",
    "location":         "Pune, Maharashtra, India",
    "zipcode":          "425001",

    # Online profiles
    "linkedin_url":     "www.linkedin.com/in/dhiraj-more-188881257",
    "github_url":       "https://github.com/dhiraj",

    # Job details
    "job_position":     "Python Developer",
    "years_experience": "1",
    "experience":       "6 months",
    "current_ctc":      "0",
    "expected_ctc":     "400000",
    "notice_period":    "0",

    # Misc
    "willing_relocate": "Yes",
    "work_auth":        "Yes",
    "gender":           "Male",

    "cover_letter": (
        "I am a final-year Computer Engineering student at Godavari College of Engineering, "
        "Jalgaon, graduating in August 2026. I have hands-on experience in SQL Server, Python, "
        "Power BI, and data analysis. I am eager to contribute and grow as a Data Analyst / "
        "Python Developer."
    ),
}

# ------------------------------------------------------------------
# KEYWORD → ANSWER MAP  (used by linkdin_linkSaver & auto_apply)
# Add new entries here whenever you encounter an unfilled field.
# ------------------------------------------------------------------

KEYWORD_ANSWERS = {
    "first name":          PROFILE["first_name"],
    "last name":           PROFILE["last_name"],
    "full name":           PROFILE["full_name"],
    "name":                PROFILE["full_name"],
    "email":               PROFILE["email"],
    "phone":               PROFILE["phone"],
    "mobile":              PROFILE["phone"],
    "whatsapp":            PROFILE["whatsapp"],
    "contact":             PROFILE["phone"],
    "city":                PROFILE["city"],
    "location":            PROFILE["location"],
    "state":               PROFILE["state"],
    "country":             PROFILE["country"],
    "zipcode":             PROFILE["zipcode"],
    "zip":                 PROFILE["zipcode"],
    "pincode":             PROFILE["zipcode"],
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
    "salary":              PROFILE["expected_ctc"],
    "notice period":       PROFILE["notice_period"],
    "notice":              PROFILE["notice_period"],
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
}

# ------------------------------------------------------------------
# BOT-DETECTION AVOIDANCE  —  random delay range (seconds)
# ------------------------------------------------------------------

DELAY_MIN = 2.5   # minimum wait between actions
DELAY_MAX = 6.0   # maximum wait between actions