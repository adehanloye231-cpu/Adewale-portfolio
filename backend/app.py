"""
Portfolio Backend Server
- Serves static frontend files
- Handles contact form submissions via POST /api/contact
- Stores submissions in backend/data/contact_submissions.json
- Admin dashboard at /admin to view submissions (password-protected)
- SENDS EMAIL NOTIFICATION to your Gmail when someone submits the form
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os
import re
import smtplib
import sys
import threading
import traceback
import urllib.request
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import html as html_module



if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "contact_submissions.json"

import os as _os_app

# Load .env file if present
_env_file = FRONTEND_DIR / ".env"
if _env_file.exists():
    try:
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k = _k.strip()
                    _v = _v.strip().strip('"\'')
                    if _k and _k not in _os_app.environ:
                        _os_app.environ[_k] = _v
    except Exception:
        pass

_DEFAULT_ADMIN_PASSWORD = "admin123"
ADMIN_PASSWORD_ENV_RAW = _os_app.environ.get("ADEWALE_ADMIN_PASSWORD", "")
if isinstance(ADMIN_PASSWORD_ENV_RAW, str) and ADMIN_PASSWORD_ENV_RAW.strip() != "":
    ADMIN_PASSWORD = ADMIN_PASSWORD_ENV_RAW.strip()
else:
    ADMIN_PASSWORD = _DEFAULT_ADMIN_PASSWORD

DATA_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

try:
    from . import config as email_config
except ImportError:
    try:
        import config as email_config
    except ImportError:
        email_config = None

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)
CORS(app)


def load_submissions():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_submissions(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def is_valid_email(email):
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email))


def is_email_configured():
    if email_config is None:
        return False
    return bool(
        getattr(email_config, "YOUR_EMAIL_ADDRESS", None)
        and getattr(email_config, "EMAIL_APP_PASSWORD", None)
    )


def looks_like_app_password(pw):
    if not pw:
        return False
    clean = pw.replace(" ", "")
    if len(clean) != 16:
        return False
    return clean.isalpha()


def html_escape(s):
    if s is None:
        return ""
    return html_module.escape(str(s))


def build_email_html(submission):
    time_local = html_escape(datetime.fromisoformat(submission["timestamp"]).strftime("%B %d, %Y at %I:%M %p"))
    escaped_name = html_escape(submission['name'])
    escaped_email = html_escape(submission['email'])
    escaped_subject = html_escape(submission['subject'])
    escaped_message = html_escape(submission['message'])
    escaped_ip = html_escape(submission.get('ip_address','N/A'))
    escaped_id = html_escape(submission['id'])
    return (
        "<!DOCTYPE html><html><head><style>"
        "body{font-family:Segoe UI,Arial,sans-serif;background:#f3f5fa;margin:0;padding:30px 15px;}"
        ".wrapper{max-width:600px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 12px 30px rgba(0,0,0,0.08);}"
        ".header{background:linear-gradient(135deg,#0e1422 0%,#101624 100%);color:#fff;padding:30px 35px;border-bottom:5px solid #19f59c;}"
        ".header h1{margin:0;font-size:24px;letter-spacing:.5px;}"
        ".header h1 span{color:#19f59c;}"
        ".tagline{color:#a6b0c4;font-size:13px;margin-top:6px;}"
        ".body{padding:30px 35px;}"
        ".info-row{display:flex;padding:14px 0;border-bottom:1px solid #eef0f6;}"
        ".info-row:last-of-type{border-bottom:none;}"
        ".label{width:110px;font-weight:700;color:#444b5e;font-size:14px;flex-shrink:0;}"
        ".value{flex:1;color:#1a1f2e;font-size:14px;line-height:1.5;word-break:break-word;}"
        ".value a{color:#0d8b5f;text-decoration:none;font-weight:600;}"
        ".value a:hover{text-decoration:underline;}"
        ".message-block{margin-top:20px;padding:20px;background:#f6fafb;border-left:4px solid #19f59c;border-radius:0 8px 8px 0;}"
        ".message-block h3{margin:0 0 12px 0;color:#0d8b5f;font-size:14px;text-transform:uppercase;letter-spacing:1px;}"
        ".message-block p{margin:0;color:#2a3042;line-height:1.7;white-space:pre-wrap;font-size:15px;}"
        ".footer{padding:20px 35px;background:#f7f8fc;font-size:12px;color:#7c869a;text-align:center;border-top:1px solid #eef0f6;}"
        ".footer code{background:#e8ecf5;padding:2px 7px;border-radius:4px;color:#444b5e;font-size:11px;}"
        "</style></head><body><div class=\"wrapper\">"
        "<div class=\"header\"><h1>New Message from your <span>Portfolio</span></h1>"
        "<div class=\"tagline\">Someone got in touch through your website contact form</div></div>"
        "<div class=\"body\">"
        "<div class=\"info-row\"><div class=\"label\">Name</div><div class=\"value\">" + escaped_name + "</div></div>"
        "<div class=\"info-row\"><div class=\"label\">Email</div><div class=\"value\"><a href=\"mailto:" + urllib.parse.quote(submission['email'], safe='@') + "?subject=" + urllib.parse.quote("Re: " + submission['subject'], safe='') + "\">" + escaped_email + "</a></div></div>"
        "<div class=\"info-row\"><div class=\"label\">Subject</div><div class=\"value\"><strong>" + escaped_subject + "</strong></div></div>"
        "<div class=\"info-row\"><div class=\"label\">Time</div><div class=\"value\">" + time_local + "</div></div>"
        "<div class=\"info-row\"><div class=\"label\">IP Address</div><div class=\"value\"><code>" + escaped_ip + "</code></div></div>"
        "<div class=\"message-block\"><h3>Message</h3><p>" + escaped_message + "</p></div>"
        "</div>"
        "<div class=\"footer\">Submission ID: <code>" + escaped_id + "</code><br>A copy of this message is also stored in your admin dashboard at /admin</div>"
        "</div></body></html>"
    )


def is_resend_configured():
    if email_config is None:
        return False
    key = getattr(email_config, "RESEND_API_KEY", "") or _os_app.environ.get("RESEND_API_KEY", "")
    return bool(key and str(key).strip().startswith("re_"))


def try_send_resend(submission):
    try:
        api_key = (
            getattr(email_config, "RESEND_API_KEY", "")
            or _os_app.environ.get("RESEND_API_KEY", "")
        ).strip()
        if not api_key:
            return False

        to_email = (
            getattr(email_config, "RESEND_TO_EMAIL", "")
            or getattr(email_config, "YOUR_EMAIL_ADDRESS", "")
            or _os_app.environ.get("RESEND_TO_EMAIL", "")
            or _os_app.environ.get("ADEWALE_GMAIL_ADDRESS", "")
            or "adehanloyemail@gmail.com"
        ).strip()

        from_email = (
            getattr(email_config, "RESEND_FROM_EMAIL", "")
            or _os_app.environ.get("RESEND_FROM_EMAIL", "")
            or "Portfolio Contact <onboarding@resend.dev>"
        ).strip()

        short_sub = submission["subject"] if len(submission["subject"]) < 50 else submission["subject"][:50] + "..."
        subject = f"{getattr(email_config, 'EMAIL_SUBJECT_PREFIX', '[PORTFOLIO CONTACT]')} {short_sub} - from {submission['name']}"

        html_body = build_email_html(submission)
        text_body = (
            "New portfolio contact message!\n\n"
            f"Name: {submission['name']}\n"
            f"Email: {submission['email']}\n"
            f"Subject: {submission['subject']}\n"
            f"Time: {submission['timestamp']}\n"
            f"IP: {submission.get('ip_address', 'N/A')}\n\n"
            f"--- MESSAGE ---\n{submission['message']}\n"
        )

        payload = json.dumps({
            "from": from_email,
            "to": [to_email],
            "reply_to": submission["email"],
            "subject": subject,
            "html": html_body,
            "text": text_body
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AdewalePortfolio/1.0"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            if 200 <= resp.status < 300:
                print(f"[EMAIL] RESEND SUCCESS: Notification sent to {to_email}")
                return True
            else:
                print(f"[EMAIL] RESEND FAILED status {resp.status}: {resp_body[:300]}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        print(f"[EMAIL] RESEND HTTP {e.code} ERROR: {err_msg[:400]}")
        return False
    except Exception as e:
        print(f"[EMAIL] RESEND ERROR: {type(e).__name__}: {str(e)[:300]}")
        return False


def is_formspree_configured():
    if email_config is None:
        return False
    fid = getattr(email_config, "FORMSPREE_FORM_ID", None)
    return bool(fid and str(fid).strip())


def try_send_formspree(submission):
    try:
        fid = str(getattr(email_config, "FORMSPREE_FORM_ID", "")).strip()
        if not fid:
            return False
        url = "https://formspree.io/f/" + fid
        payload = urllib.parse.urlencode({
            "name": submission["name"],
            "email": submission["email"],
            "_replyto": submission["email"],
            "_subject": (getattr(email_config, "EMAIL_SUBJECT_PREFIX", "") + " " + submission["subject"]).strip(),
            "subject": submission["subject"],
            "message": submission["message"],
            "ip_address": submission.get("ip_address", "N/A"),
            "timestamp": submission["timestamp"],
            "_gotcha": ""
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if 200 <= resp.status < 300:
                print("[EMAIL] FORMSPREE SUCCESS: Submission sent to Formspree -> " + getattr(email_config, "YOUR_EMAIL_ADDRESS", "(your email)"))
                return True
            else:
                print("[EMAIL] FORMSPREE FAILED status " + str(resp.status) + ": " + body[:300])
                return False
    except Exception as e:
        print("[EMAIL] FORMSPREE FAILED: " + type(e).__name__ + ": " + str(e)[:300])
        return False


def try_send_smtp(submission):
    sender = email_config.EMAIL_SENDER or email_config.YOUR_EMAIL_ADDRESS
    receiver = email_config.EMAIL_RECEIVER or email_config.YOUR_EMAIL_ADDRESS
    app_password = email_config.EMAIL_APP_PASSWORD

    msg = MIMEMultipart("alternative")
    msg["From"] = "Adewale Portfolio <" + sender + ">"
    msg["To"] = receiver
    msg["Reply-To"] = submission["email"]
    short_subject = submission["subject"] if len(submission["subject"]) < 50 else submission["subject"][:50] + "..."
    msg["Subject"] = getattr(email_config, "EMAIL_SUBJECT_PREFIX", "[PORTFOLIO]") + " " + short_subject + " - from " + submission["name"]

    text_body = (
        "New portfolio contact message!\n\n"
        "Name: " + submission["name"] + "\n"
        "Email: " + submission["email"] + "\n"
        "Subject: " + submission["subject"] + "\n"
        "Time: " + submission["timestamp"] + "\n"
        "IP: " + submission.get("ip_address", "N/A") + "\n\n"
        "--- MESSAGE ---\n" + submission["message"] + "\n"
    )
    html_body = build_email_html(submission)
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    smtp_server = getattr(email_config, "EMAIL_SMTP_SERVER", "smtp.gmail.com")
    ports = getattr(email_config, "EMAIL_PORTS_TO_TRY", [587, 465])

    last_err = None
    for port in ports:
        port = int(port)
        server = None
        try:
            print("[EMAIL] Trying SMTP " + smtp_server + ":" + str(port) + " ...")
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=30)
                server.ehlo()
                try:
                    server.starttls()
                    server.ehlo()
                except smtplib.SMTPException:
                    pass
            server.login(sender, app_password)
            server.sendmail(sender, [receiver], msg.as_string())
            try:
                server.quit()
            except Exception:
                pass
            print("[EMAIL] SMTP SUCCESS on port " + str(port) + ": Notification sent to " + receiver)
            return True
        except smtplib.SMTPAuthenticationError as e:
            code = getattr(e, "smtp_code", "?")
            print("[EMAIL] SMTP port " + str(port) + " AUTH FAILED (SMTP " + str(code) + ")")
            last_err = e
            try:
                server.quit()
            except Exception:
                pass
        except Exception as e:
            print("[EMAIL] SMTP port " + str(port) + " FAILED: " + type(e).__name__ + ": " + str(e)[:200])
            last_err = e
            try:
                server.quit()
            except Exception:
                pass

    if isinstance(last_err, smtplib.SMTPAuthenticationError):
        print("")
        print("=" * 68)
        print("  GOOGLE REJECTED YOUR APP PASSWORD (SMTP 535 BadCredentials)")
        print("=" * 68)
        print("  MOST LIKELY REASONS (fix these in order):")
        print("")
        print("  1. 2-Step Verification NOT enabled on your Google account")
        print("     -> Go here and TURN IT ON first:")
        print("        https://myaccount.google.com/signinoptions/two-step-verification")
        print("")
        print("  2. App Password was NOT generated with Mail+Windows combo")
        print("     -> Delete old ones + regenerate FRESH one here:")
        print("        https://myaccount.google.com/apppasswords")
        print("        (Select app: Mail, Select device: Windows Computer)")
        print("")
        print("  3. Google blocked first sign-in from this new device/IP")
        print("     -> FIRST visit: https://accounts.google.com/DisplayUnlockCaptcha")
        print("        Click 'Continue' to allow new sign-ins, then try again.")
        print("")
        print("  4. You have a Workspace / business Gmail with admin-locked SMTP")
        print("     -> Use Formspree fallback instead (FREE, no App Password)")
        print("        Sign up: https://formspree.io  -> takes 60 seconds")
        print("")
        print("  5. Wrong account: The App Password was created for a different Gmail")
        configured_email = (
            (email_config.YOUR_EMAIL_ADDRESS if email_config else "") or "(your Gmail in .env)"
        )
        print("     -> Must be created for: " + configured_email)
        print("=" * 68)
        print("")
    return False


def send_contact_email(submission):
    # 1. Try Resend FIRST (recommended modern API for Vercel & cloud)
    if is_resend_configured():
        print("[EMAIL] Attempting to send notification via Resend...")
        if try_send_resend(submission):
            return True
        print("[EMAIL] Resend attempt failed. Checking fallbacks...")

    # 2. Try Gmail SMTP
    smtp_ok = False
    if is_email_configured():
        pw = email_config.EMAIL_APP_PASSWORD
        if not looks_like_app_password(pw):
            print("[EMAIL] INVALID App Password format: " + repr(pw))
            print("        Must be EXACTLY 16 lowercase letters (no spaces, no symbols)")
            print("        Generate one: https://myaccount.google.com/apppasswords")
        else:
            smtp_ok = try_send_smtp(submission)
    else:
        print("[EMAIL] Gmail SMTP not configured (no App Password in config.py)")

    if smtp_ok:
        return True

    # 3. Try Formspree fallback
    if is_formspree_configured():
        print("[EMAIL] Falling back to Formspree...")
        return try_send_formspree(submission)

    print("[EMAIL] No email delivery method succeeded.")
    print("        Messages are still being saved to the database (see /admin dashboard).")
    print("        Add RESEND_API_KEY in .env or Vercel Environment Variables,")
    print("        or fix Gmail SMTP by setting ADEWALE_GMAIL_APP_PASSWORD in .env.")
    return False




def send_auto_reply_email(submission):
    if email_config is None or not is_email_configured():
        return
    try:
        sender=email_config.EMAIL_SENDER or email_config.YOUR_EMAIL_ADDRESS
        receiver=submission["email"]
        msg=MIMEMultipart("alternative")
        msg["From"]="Adewale Portfolio <{}>".format(sender)
        msg["To"]=receiver
        msg["Subject"]="Thank You for Contacting Adehanloye Adewale"
        body=f"""Hello {submission['name']},

Thank you for contacting me through my portfolio website.

I have received your message regarding:
"{submission['subject']}"

I will get back to you as soon as possible.

Best regards,
Adehanloye Adewale
"""
        msg.attach(MIMEText(body,"plain","utf-8"))
        server=smtplib.SMTP("smtp.gmail.com",587,timeout=30)
        server.starttls();server.login(sender,email_config.EMAIL_APP_PASSWORD)
        server.sendmail(sender,[receiver],msg.as_string());server.quit()
    except Exception as e:
        print("[AUTO REPLY]",e)



def send_contact_email_async(submission):
    t = threading.Thread(target=send_contact_email, args=(submission,), daemon=True)
    t.start()



@app.route("/api/contact", methods=["POST"])
def contact():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Invalid request format. Please send JSON data."
        }), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    errors = []
    if not name:
        errors.append("Name is required.")
    elif len(name) > 100:
        errors.append("Name is too long (max 100 characters).")

    if not email:
        errors.append("Email is required.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    elif len(email) > 150:
        errors.append("Email is too long (max 150 characters).")

    if not subject:
        errors.append("Subject is required.")
    elif len(subject) > 200:
        errors.append("Subject is too long (max 200 characters).")

    if not message:
        errors.append("Message is required.")
    elif len(message) > 5000:
        errors.append("Message is too long (max 5000 characters).")

    if errors:
        return jsonify({
            "success": False,
            "message": " ".join(errors),
            "errors": errors
        }), 400

    submission = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "Unknown")
    }

    submissions = load_submissions()
    submissions.insert(0, submission)
    save_submissions(submissions)

    send_contact_email_async(submission)
    threading.Thread(target=send_auto_reply_email,args=(submission,),daemon=True).start()

    return jsonify({
        "success": True,
        "message": "Your message has been sent successfully. I'll get back to you soon!",
        "id": submission["id"],
        "timestamp": submission["timestamp"]
    }), 201


@app.route("/api/submissions", methods=["GET"])
def get_submissions():
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({
            "success": False,
            "message": "Unauthorized. Invalid admin password."
        }), 401

    submissions = load_submissions()
    return jsonify({
        "success": True,
        "count": len(submissions),
        "submissions": submissions
    })


ADMIN_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Admin - Contact Submissions</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Poppins,sans-serif;}
body{background:#090d17;color:#fff;min-height:100vh;padding:40px 5%;}
.container{max-width:1200px;margin:0 auto;}
h1{color:#19f59c;font-size:36px;margin-bottom:10px;}
.subtitle{color:#a6a6a6;margin-bottom:40px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:40px;}
.stat-card{background:#101624;padding:25px;border-radius:12px;border:1px solid #22293b;}
.stat-card h3{color:#a6a6a6;font-size:14px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
.stat-card p{color:#19f59c;font-size:32px;font-weight:700;}
.login-box{max-width:400px;margin:80px auto;background:#101624;padding:40px;border-radius:16px;border:1px solid #22293b;}
.login-box input{width:100%;padding:15px;margin-bottom:20px;background:#1b2233;border:2px solid #22293b;color:#fff;border-radius:8px;font-size:16px;}
.login-box input:focus{outline:none;border-color:#19f59c;}
.login-box button{width:100%;padding:15px;background:#19f59c;color:#000;border:none;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;}
.submissions-list{display:flex;flex-direction:column;gap:20px;}
.submission{background:#101624;padding:25px;border-radius:12px;border-left:5px solid #19f59c;border:1px solid #22293b;transition:all .3s;}
.submission:hover{transform:translateY(-3px);border-color:#19f59c;box-shadow:0 10px 30px rgba(25,245,156,.15);}
.sub-header{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:15px;}
.sub-name{font-size:20px;font-weight:600;color:#fff;}
.sub-email{color:#19f59c;font-size:14px;}
.sub-time{color:#a6a6a6;font-size:13px;}
.sub-subject{font-size:17px;font-weight:600;color:#fff;margin-bottom:10px;padding:10px 15px;background:#1b2233;border-radius:6px;}
.sub-message{color:#d1d1d1;line-height:1.7;white-space:pre-wrap;word-break:break-word;}
.sub-meta{margin-top:15px;padding-top:15px;border-top:1px solid #22293b;font-size:12px;color:#888;}
.empty{text-align:center;padding:60px 20px;color:#a6a6a6;}
.empty .ic{font-size:60px;margin-bottom:15px;opacity:.4;}
.logout-btn{margin-bottom:30px;padding:10px 20px;background:transparent;color:#ff4444;border:2px solid #ff4444;border-radius:8px;cursor:pointer;font-weight:600;}
.alert{padding:15px 20px;margin-bottom:25px;border-radius:10px;background:#2a1010;border:1px solid #ff4444;color:#ffb3b3;font-size:14px;line-height:1.6;}
.alert strong{color:#ff4444;display:block;font-size:15px;margin-bottom:6px;}
.alert ol{padding-left:20px;margin-top:8px;}
.alert ol li{margin-bottom:4px;}
.alert a{color:#19f59c;}
.setup-info{background:#101a20;border:1px solid #19f59c44;border-radius:10px;padding:20px;margin-bottom:30px;}
.setup-info h3{color:#19f59c;font-size:16px;margin-bottom:10px;}
.setup-info p,.setup-info li{color:#c1d0e0;font-size:13px;line-height:1.7;}
.setup-info ol{padding-left:22px;}
.status{display:inline-block;padding:4px 12px;border-radius:50px;font-size:12px;font-weight:700;margin-left:10px;}
.status.on{background:#19f59c22;color:#19f59c;border:1px solid #19f59c;}
.status.off{background:#ff444422;color:#ff8888;border:1px solid #ff4444;}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">
</head>
<body><div class="container"><div id="app"></div></div>
<script>
window.__PORTFOLIO_CFG__ = (function(){
    var e = (typeof __ADMIN_EMAIL__ !== 'undefined') ? String(__ADMIN_EMAIL__ || '') : '';
    var d = (typeof __ADMIN_DEFAULT_PW__ !== 'undefined') ? String(__ADMIN_DEFAULT_PW__ || '') : '';
    return { configuredEmail: e || 'your Gmail address (set ADEWALE_GMAIL_ADDRESS in .env)', defaultAdminHint: d };
})();
</script>
<script>
const app=document.getElementById('app');
const SK='admin_auth_pw';
function logout(){localStorage.removeItem(SK);render();}
function escapeHtml(s){const d=document.createElement('div');d.textContent=String(s||'');return d.innerHTML;}

function emailSetupAlert(){
    var _email = (window.__PORTFOLIO_CFG__ && window.__PORTFOLIO_CFG__.configuredEmail) || 'your Gmail address (set ADEWALE_GMAIL_ADDRESS in .env)';
    return '<div class="alert"><strong><i class="fas fa-exclamation-triangle"></i> EMAIL NOTIFICATIONS NOT SET UP</strong>'
    +'Messages are being saved to the JSON database below, but emails are NOT being sent to your Gmail yet.<br>'
    +'Your server detected the password you entered is NOT a valid Google App Password.<br><br>'
    +'<strong>Follow these EXACT steps:</strong><ol>'
    +'<li>Open <a href="https://myaccount.google.com/" target="_blank">https://myaccount.google.com/</a> and log in as <code>'+_email+'</code></li>'
    +'<li>Click <strong>Security</strong> on the left sidebar</li>'
    +'<li>Under <strong>"How you sign in to Google"</strong> → turn <strong>ON 2-Step Verification</strong> (required!)</li>'
    +'<li>After 2FA is on, <strong>search the page for "App passwords"</strong> (use Ctrl+F)</li>'
    +'<li>Click <strong>App passwords</strong> → Select app: <strong>Mail</strong>, Select device: <strong>Windows Computer</strong> → <strong>Generate</strong></li>'
    +'<li>Copy the 16-letter password (looks like: <code>abcd efgh ijkl mnop</code>) — <strong>no spaces, no symbols</strong></li>'
    +'<li>Open the <code>.env</code> file in the project root (NOT config.py) and add the line: <code>ADEWALE_GMAIL_APP_PASSWORD=abcdefghijklmnop</code></li>'
    +'<li>Restart the Python server (Ctrl+C then re-run: <code>py backend\\\\app.py</code> or <code>npm start</code>)</li>'
    +'</ol></div>';
}

function renderLogin(msg=''){
    app.innerHTML='<div class="login-box">'
    +'<h1 style="text-align:center;font-size:28px;margin-bottom:8px;"><i class="fas fa-lock"></i> Admin Login</h1>'
    +'<p class="subtitle" style="text-align:center;margin-bottom:30px;">Enter admin password to view submissions</p>'
    +(msg?'<p style="color:#ff4444;margin-bottom:20px;text-align:center;">'+escapeHtml(msg)+'</p>':'')
    +'<form id="loginForm"><input type="password" id="pw" placeholder="Enter Password" required>'
    +'<button type="submit">Login</button></form>'
    +'<p style="text-align:center;margin-top:20px;color:#888;font-size:13px;">Default (set in .env ADEWALE_ADMIN_PASSWORD): '
    +'admin123'
    +'</p></div>';
    document.getElementById('loginForm').onsubmit=e=>{e.preventDefault();
        const pw=document.getElementById('pw').value;
        fetch('/api/submissions?password='+encodeURIComponent(pw))
        .then(r=>r.json()).then(d=>{
            if(d.success){localStorage.setItem(SK,pw);render();}
            else renderLogin(d.message);});};
}

function renderDashboard(){
    const pw=localStorage.getItem(SK);
    fetch('/api/submissions?password='+encodeURIComponent(pw))
    .then(r=>r.json()).then(async d=>{
        if(!d.success){localStorage.removeItem(SK);renderLogin();return;}
        let setupInfo='';let emailStatus='<span class="status off">OFF</span>';
        try{
            const cfg=await fetch('/api/email-check?password='+encodeURIComponent(pw)).then(r=>r.json());
            if(cfg.email_configured && cfg.valid_format){emailStatus='<span class="status on">ON</span>';}
            else if(cfg.email_configured && !cfg.valid_format){setupInfo=emailSetupAlert();}
        }catch(e){}
        const total=d.count;
        const today=new Date().toDateString();
        const todayCount=d.submissions.filter(s=>new Date(s.timestamp).toDateString()===today).length;
        const uniqueEmails=new Set(d.submissions.map(s=>s.email)).size;
        app.innerHTML='<button class="logout-btn" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Logout</button>'
        +'<h1><i class="fas fa-inbox"></i> Contact Submissions '+emailStatus+'</h1>'
        +'<p class="subtitle">All messages received from your portfolio contact form</p>'
        +setupInfo
        +'<div class="stats">'
        +'<div class="stat-card"><h3>Total Messages</h3><p>'+total+'</p></div>'
        +'<div class="stat-card"><h3>Today</h3><p>'+todayCount+'</p></div>'
        +'<div class="stat-card"><h3>Unique Senders</h3><p>'+uniqueEmails+'</p></div></div>'
        +'<div class="submissions-list" id="sublist"></div>';
        const list=document.getElementById('sublist');
        if(total===0){
            list.innerHTML='<div class="empty"><div class="ic"><i class="fas fa-envelope-open"></i></div>'
            +'<p>No submissions yet. Messages from your portfolio contact form will appear here.</p></div>';
            return;}
        list.innerHTML=d.submissions.map(s=>'<div class="submission">'
        +'<div class="sub-header"><div>'
        +'<div class="sub-name"><i class="fas fa-user-circle"></i> '+escapeHtml(s.name)+'</div>'
        +'<a class="sub-email" href="mailto:'+escapeHtml(s.email)+'?subject=Re:'+encodeURIComponent(s.subject)+'"><i class="fas fa-envelope"></i> '+escapeHtml(s.email)+'</a></div>'
        +'<div class="sub-time"><i class="fas fa-clock"></i> '+new Date(s.timestamp).toLocaleString()+'</div></div>'
        +'<div class="sub-subject"><i class="fas fa-tag"></i> '+escapeHtml(s.subject)+'</div>'
        +'<div class="sub-message">'+escapeHtml(s.message)+'</div>'
        +'<div class="sub-meta"><i class="fas fa-globe"></i> IP: '+escapeHtml(s.ip_address||'N/A')+' &nbsp;|&nbsp; ID: '+escapeHtml(s.id)+'</div></div>').join('');
    });
}

function render(){
    if(localStorage.getItem(SK))renderDashboard();
    else renderLogin();
}
render();
</script></body></html>"""


@app.route("/admin")
def admin():
    import json as _json_safe
    cfg_email = (email_config.YOUR_EMAIL_ADDRESS if email_config else "") or ""
    safe_email_js_literal = _json_safe.dumps(str(cfg_email), ensure_ascii=True)
    safe_default_pw_js_literal = _json_safe.dumps(str(_DEFAULT_ADMIN_PASSWORD), ensure_ascii=True)
    prefix = (
        "<script>"
        "var __ADMIN_EMAIL__ = " + safe_email_js_literal + ";"
        "var __ADMIN_DEFAULT_PW__ = " + safe_default_pw_js_literal + ";"
        "</script>"
    )
    body_with_default_hint = ADMIN_HTML.replace(
        "'admin123'",
        "(window.__PORTFOLIO_CFG__ && window.__PORTFOLIO_CFG__.defaultAdminHint) || 'admin123'",
        1,
    )
    return render_template_string(prefix + body_with_default_hint)


@app.route("/api/email-check", methods=["GET"])
def email_check():
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    cfg = email_config
    addr = getattr(cfg, "YOUR_EMAIL_ADDRESS", None) if cfg else None
    pw = getattr(cfg, "EMAIL_APP_PASSWORD", None) if cfg else None
    return jsonify({
        "success": True,
        "email_configured": bool(addr and pw),
        "email_address": addr,
        "password_length": len(pw) if pw else 0,
        "valid_format": looks_like_app_password(pw) if pw else False
    })


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")


if __name__ == "__main__":
    PORT = 5000
    if ADMIN_PASSWORD == _DEFAULT_ADMIN_PASSWORD:
        _admin_pw_line = "  Admin pw:   DEFAULT (set ADEWALE_ADMIN_PASSWORD in .env)"
        _admin_pw_line += "\n              Current: 'admin123' (change in .env for production!)"
    else:
        _hidden = "*" * max(6, min(16, len(ADMIN_PASSWORD)))
        _admin_pw_line = "  Admin pw:   SET (from .env ADEWALE_ADMIN_PASSWORD) -> " + _hidden
    print("=" * 60)
    print("  ADEWALE PORTFOLIO BACKEND SERVER")
    print("=" * 60)
    print("  Website:    http://localhost:" + str(PORT) + "/")
    print("  Admin:      http://localhost:" + str(PORT) + "/admin")
    print("  API:        POST http://localhost:" + str(PORT) + "/api/contact")
    print("  Data file:  " + str(DATA_FILE))
    print(_admin_pw_line)

    if is_resend_configured():
        to_addr = getattr(email_config, "RESEND_TO_EMAIL", None) or "adehanloyemail@gmail.com"
        print("  Email:      READY (Resend API) -> " + str(to_addr))
    elif is_email_configured():
        pw = email_config.EMAIL_APP_PASSWORD
        if looks_like_app_password(pw):
            print("  Email:      READY (Gmail SMTP) -> " + str(email_config.YOUR_EMAIL_ADDRESS))
        else:
            print("  Email:      INVALID Gmail App Password! (Consider using RESEND_API_KEY instead)")
    else:
        print("  Email:      NOT CONFIGURED (set RESEND_API_KEY in .env or Vercel)")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=PORT, debug=False)
