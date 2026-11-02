"""
================================================================
            EMAIL CONFIGURATION SETTINGS
================================================================

THREE EMAIL SENDING METHODS ARE AVAILABLE:

METHOD 1) RESEND API (Recommended - Works on Vercel & Locally)
        - REQUIRES: Free account at https://resend.com
        - Copy your API key (starts with "re_")
        - In Vercel: Add RESEND_API_KEY in Project Settings > Environment Variables
        - Free tier sends up to 3,000 emails/month!

METHOD 2) GMAIL SMTP (Local Fallback)
        - REQUIRES: 2-Step Verification ON + 16-char App Password

METHOD 3) FORMSPREE FALLBACK
        - Free account at https://formspree.io
"""

import os

# ================================================================
# METHOD 1 - RESEND API SETTINGS (RECOMMENDED)
# ================================================================
# Get free API key from https://resend.com
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

# Default free-tier test sender (works immediately without custom domain)
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "Portfolio Contact <onboarding@resend.dev>")

# Where you receive notifications
RESEND_TO_EMAIL = os.environ.get("RESEND_TO_EMAIL", "adehanloyemail@gmail.com")

# ================================================================
# METHOD 2 - GMAIL SMTP SETTINGS (LEGACY)
# ================================================================
YOUR_EMAIL_ADDRESS = os.environ.get("ADEWALE_GMAIL_ADDRESS", "adehanloyemail@gmail.com")
EMAIL_APP_PASSWORD = os.environ.get("ADEWALE_GMAIL_APP_PASSWORD", "jogaoiehnqzlhboy")

EMAIL_SMTP_SERVER = os.environ.get("ADEWALE_GMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_PORTS_TO_TRY = [587, 465]

EMAIL_SENDER = YOUR_EMAIL_ADDRESS
EMAIL_RECEIVER = YOUR_EMAIL_ADDRESS
EMAIL_SUBJECT_PREFIX = os.environ.get("ADEWALE_EMAIL_SUBJECT_PREFIX", "[PORTFOLIO CONTACT]")

# ================================================================
# METHOD 3 - FORMSPREE FALLBACK
# ================================================================
FORMSPREE_FORM_ID = os.environ.get("ADEWALE_FORMSPREE_FORM_ID", "mzedjaqe")
