/**
 * Vercel Serverless Function: POST /api/contact
 * Handles contact form submissions and delivers emails using Resend.
 */

const { Resend } = require('resend');

// Helper to escape HTML to prevent XSS in email body
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

module.exports = async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Only POST is allowed for form submission
  if (req.method !== 'POST') {
    return res.status(405).json({
      success: false,
      message: 'Method not allowed. Use POST to submit the contact form.'
    });
  }

  // Parse body safely
  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch (e) {
      return res.status(400).json({
        success: false,
        message: 'Invalid JSON request format.'
      });
    }
  }
  body = body || {};

  const name = (body.name || '').trim();
  const email = (body.email || '').trim();
  const subject = (body.subject || '').trim();
  const message = (body.message || '').trim();

  // Validate required fields
  const errors = [];
  if (!name) errors.push('Name is required.');
  else if (name.length > 100) errors.push('Name is too long (max 100 characters).');

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) errors.push('Email is required.');
  else if (!emailRegex.test(email)) errors.push('Please enter a valid email address.');
  else if (email.length > 150) errors.push('Email is too long (max 150 characters).');

  if (!subject) errors.push('Subject is required.');
  else if (subject.length > 200) errors.push('Subject is too long (max 200 characters).');

  if (!message) errors.push('Message is required.');
  else if (message.length > 5000) errors.push('Message is too long (max 5000 characters).');

  if (errors.length > 0) {
    return res.status(400).json({
      success: false,
      message: errors.join(' '),
      errors
    });
  }

  // Verify Resend API Key
  const apiKey = (process.env.RESEND_API_KEY || '').trim();
  if (!apiKey) {
    console.error('[API/CONTACT] RESEND_API_KEY environment variable is missing.');
    return res.status(500).json({
      success: false,
      message: 'Server configuration error: RESEND_API_KEY is not set in Vercel environment variables. Please add RESEND_API_KEY in your Vercel Project Settings > Environment Variables.'
    });
  }

  // Configuration for recipient and sender
  const toEmail = (
    process.env.RESEND_TO_EMAIL ||
    process.env.RECEIVER_EMAIL ||
    process.env.ADEWALE_GMAIL_ADDRESS ||
    'adehanloye231@gmail.com'
  ).trim();

  // Resend provides "onboarding@resend.dev" for free tier testing before domain verification.
  // Once a custom domain is verified in Resend, RESEND_FROM_EMAIL can be set (e.g. "contact@yourdomain.com")
  const fromEmail = (
    process.env.RESEND_FROM_EMAIL ||
    'Portfolio Contact <onboarding@resend.dev>'
  ).trim();

  const formattedTime = new Date().toLocaleString('en-US', {
    dateStyle: 'full',
    timeStyle: 'medium',
    timeZone: 'UTC'
  }) + ' UTC';

  const safeName = escapeHtml(name);
  const safeEmail = escapeHtml(email);
  const safeSubject = escapeHtml(subject);
  const safeMessage = escapeHtml(message);

  const emailSubject = `Portfolio Message from ${name}: ${subject.slice(0, 50)}`;

  const htmlBody = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; margin: 0; padding: 30px 15px; color: #ffffff; }
    .container { max-width: 600px; margin: 0 auto; background-color: #111726; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
    .header { background: linear-gradient(135deg, #0e1422 0%, #172238 100%); padding: 30px; border-bottom: 3px solid #19f59c; }
    .header h1 { margin: 0; font-size: 22px; color: #ffffff; }
    .header h1 span { color: #19f59c; }
    .header p { margin: 6px 0 0; font-size: 14px; color: #94a3b8; }
    .content { padding: 30px; }
    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .info-table td { padding: 10px 0; border-bottom: 1px solid #1e293b; font-size: 14px; vertical-align: top; }
    .info-table td.label { width: 110px; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }
    .info-table td.value { color: #f1f5f9; }
    .info-table td.value a { color: #19f59c; text-decoration: none; font-weight: 600; }
    .message-box { background-color: #0b0f19; border-left: 4px solid #19f59c; padding: 20px; border-radius: 0 8px 8px 0; margin-top: 15px; }
    .message-box h3 { margin: 0 0 10px; color: #19f59c; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .message-box p { margin: 0; color: #e2e8f0; line-height: 1.6; font-size: 15px; white-space: pre-wrap; word-break: break-word; }
    .action-btn { display: inline-block; margin-top: 25px; padding: 12px 24px; background-color: #19f59c; color: #090d17; font-weight: 700; text-decoration: none; border-radius: 6px; font-size: 14px; }
    .footer { padding: 20px 30px; background-color: #0b0f19; border-top: 1px solid #1e293b; text-align: center; font-size: 12px; color: #64748b; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>New Message from your <span>Portfolio</span></h1>
      <p>Someone reached out through your contact form</p>
    </div>
    <div class="content">
      <table class="info-table">
        <tr>
          <td class="label">Sender Name</td>
          <td class="value"><strong>${safeName}</strong></td>
        </tr>
        <tr>
          <td class="label">Email Address</td>
          <td class="value"><a href="mailto:${safeEmail}">${safeEmail}</a></td>
        </tr>
        <tr>
          <td class="label">Subject</td>
          <td class="value">${safeSubject}</td>
        </tr>
        <tr>
          <td class="label">Date / Time</td>
          <td class="value">${formattedTime}</td>
        </tr>
      </table>

      <div class="message-box">
        <h3>Message Content</h3>
        <p>${safeMessage}</p>
      </div>

      <div style="text-align: center; margin-top: 25px;">
        <a href="mailto:${safeEmail}?subject=Re:%20${encodeURIComponent(subject)}" class="action-btn">
          Reply Directly to ${safeName}
        </a>
      </div>
    </div>
    <div class="footer">
      Sent automatically via Resend from your portfolio contact form.
    </div>
  </div>
</body>
</html>`;

  const textBody = `New Contact Form Message from Adewale Portfolio

Sender: ${name} (${email})
Subject: ${subject}
Date: ${formattedTime}

--- Message ---
${message}

Reply directly by emailing: ${email}`;

  try {
    const resend = new Resend(apiKey);

    const { data, error } = await resend.emails.send({
      from: fromEmail,
      to: [toEmail],
      reply_to: email,
      subject: emailSubject,
      html: htmlBody,
      text: textBody
    });

    if (error) {
      console.error('[API/CONTACT] Resend error:', error);
      return res.status(400).json({
        success: false,
        message: error.message || 'Failed to send message via Resend.',
        error
      });
    }

    console.log('[API/CONTACT] Email sent successfully via Resend. ID:', data?.id);
    return res.status(200).json({
      success: true,
      message: "Your message has been sent successfully! I'll get back to you soon.",
      id: data?.id
    });
  } catch (err) {
    console.error('[API/CONTACT] Unexpected error:', err);
    return res.status(500).json({
      success: false,
      message: 'An unexpected server error occurred while sending your message. Please try again later.'
    });
  }
};

