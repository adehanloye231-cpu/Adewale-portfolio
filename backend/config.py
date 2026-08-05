"""
================================================================
            EMAIL CONFIGURATION SETTINGS
================================================================

TWO EMAIL SENDING METHODS ARE AVAILABLE:

METHOD 1) GMAIL SMTP (Recommended) - Sends directly from your Gmail
        - REQUIRES: 2-Step Verification ON + 16-char App Password
        - Allowed from anywhere, no signup needed

METHOD 2) FORMSPREE FALLBACK - No Google App Password needed!
        - REQUIRES: Free account at https://formspree.io
        - Just paste your Formspree Form ID below
        - Sign up at https://formspree.io (takes 60 seconds, 50 emails/month free)

If both are configured, Gmail SMTP will be used first.
"""

# ================================================================
# METHOD 1 - GMAIL SMTP SETTINGS
# ================================================================

# Your full Gmail address (sender AND receiver unless overridden below)
YOUR_EMAIL_ADDRESS = "adehanloyemail@gmail.com"

# Your 16-character GOOGLE APP PASSWORD - ONLY LOWERCASE LETTERS (no spaces!)
# How to get one (REQUIRED STEPS):
#   1. https://myaccount.google.com/  →  Security
#   2. Turn ON  "2-Step Verification"  (MANDATORY - Google requires it)
#   3. Search "App passwords" on Security page (Ctrl+F)
#   4. Select app: Mail,  Select device: Windows Computer
#   5. Click GENERATE  →  Copy the 16 letters shown in the YELLOW BAR
#   6. Paste here (WITHOUT SPACES!):  jogaoiehnqzlhboy
EMAIL_APP_PASSWORD = "jogaoiehnqzlhboy"

# --- Gmail advanced ---
EMAIL_SMTP_SERVER = "smtp.gmail.com"
# Try both ports if needed (system will auto-try both)
EMAIL_PORTS_TO_TRY = [587, 465]
# 587 = STARTTLS (often works better for new setups), 465 = SSL

# Sender / Receiver can be different emails if you want
EMAIL_SENDER   = YOUR_EMAIL_ADDRESS    # Who appears as the sender
EMAIL_RECEIVER = YOUR_EMAIL_ADDRESS    # Who gets the notification

# Subject prefix for all notifications
EMAIL_SUBJECT_PREFIX = "[PORTFOLIO CONTACT]"

# ================================================================
# METHOD 2 - FORMSPREE FALLBACK  (enable if Gmail SMTP keeps failing)
# ================================================================
# Go to https://formspree.io → Create free account → Create new "Form"
# After creating, they give you a URL like:  https://formspree.io/f/xxxxyyyy
# Copy the xxxxxyyyy part below as your Form ID:
FORMSPREE_FORM_ID = ""

# Example: if your Form URL is https://formspree.io/f/mabcdxyz  then set:
# FORMSPREE_FORM_ID = "mabcdxyz"
#
# Leave EMPTY "" to disable Formspree fallback.
