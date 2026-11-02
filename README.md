# Adehanloye Adewale - Portfolio Website

A modern, responsive personal portfolio website showcasing web development and software engineering projects, skills, and resume. Features an automated contact form powered by **Resend** and serverless deployment on **Vercel**.

---

## 🚀 Features

- **Responsive Design**: Optimized for desktop, tablet, and mobile devices.
- **Interactive UI**: Typing effect, smooth scroll, scroll animations, interactive project showcases.
- **Contact Form with Resend**: Direct email delivery to your inbox via Resend API (`/api/contact`).
- **One-Click Reply**: Received emails include a `reply_to` header so you can hit "Reply" in your email client to respond directly to the sender.
- **Vercel Serverless Ready**: Automatic deployment on push with zero configuration.

---

## 📬 Setting Up Resend for the Contact Form

To receive emails from your portfolio contact form:

### 1. Get a Free Resend API Key
1. Sign up at [https://resend.com](https://resend.com) (free, up to 3,000 emails/month).
2. Go to the **API Keys** section in your Resend dashboard.
3. Click **Create API Key**, give it a name (e.g. `Portfolio`), and copy the key (starts with `re_...`).

### 2. Add the Environment Variable to Vercel
1. Open your project on [Vercel](https://vercel.com).
2. Go to **Settings** → **Environment Variables**.
3. Add:
   - **Key:** `RESEND_API_KEY`
   - **Value:** `re_your_api_key_here`
4. *(Optional)* Add `RESEND_TO_EMAIL` if you want emails sent to a specific address (defaults to `adehanloyemail@gmail.com`).
5. Click **Save** and trigger a **Redeploy** (or push a new commit to `main`).

---

## 💻 Local Development

### Option A: Local Frontend Server
```bash
npx http-server . -p 8080
```

### Option B: Local Flask Backend (with SQLite/JSON Submissions & Admin Panel)
1. Add `RESEND_API_KEY=re_...` to `.env`.
2. Run:
```bash
run_server.bat
# or
py backend/app.py
```
Visit `http://localhost:5000` to view the website and `http://localhost:5000/admin` for the local submissions dashboard.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
