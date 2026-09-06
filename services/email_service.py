import os
import smtplib
import socket
from email.message import EmailMessage
import urllib.request
import urllib.error
import json


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Delivers a 6-digit OTP verification code to the recipient email address.
    Supports Resend API, Standard SMTP, or development logging fallback.
    Development mode fallback activates ONLY when ENVIRONMENT is explicitly set to development, dev, or local.
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    is_dev = env in ("development", "dev", "local")

    resend_key = os.getenv("RESEND_API_KEY")
    smtp_host = os.getenv("SMTP_HOST")
    
    # Default sender: if using Resend without custom domain, default to onboarding@resend.dev
    default_from = "PulseScout Auth <onboarding@resend.dev>" if resend_key else "PulseScout Auth <auth@pulsescout.com>"
    sender_email = os.getenv("EMAIL_FROM", default_from)
    subject = "Your PulseScout verification code"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0e12; color: #ffffff; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: #16181f; border-radius: 16px; padding: 32px; border: 1px solid #2a2d3d; text-align: center; }}
            .logo {{ font-size: 32px; font-weight: 900; color: #ffb800; margin-bottom: 8px; }}
            .title {{ font-size: 20px; font-weight: 700; margin-bottom: 16px; color: #ffffff; }}
            .otp-box {{ background: #222634; border: 2px dashed #ffb800; border-radius: 12px; padding: 20px; font-size: 36px; font-weight: 900; letter-spacing: 8px; color: #ffb800; margin: 24px 0; }}
            .text {{ font-size: 14px; color: #a0a5b8; line-height: 1.6; margin-bottom: 24px; }}
            .footer {{ font-size: 12px; color: #606578; border-top: 1px solid #2a2d3d; padding-top: 16px; margin-top: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">⚡ PulseScout</div>
            <div class="title">Verify Your Email</div>
            <div class="text">Use the following 6-digit verification code to complete your sign-in:</div>
            <div class="otp-box">{otp}</div>
            <div class="text">This code will expire in <strong>10 minutes</strong>.<br>If you did not request this code, you can safely ignore this email.</div>
            <div class="footer">PulseScout — Personalized News. Delivered Instantly.</div>
        </div>
    </body>
    </html>
    """

    plain_content = f"""
Your PulseScout verification code is:

{otp}

This code will expire in 10 minutes.
If you did not request this code, you can safely ignore this email.
    """

    # 1. Try Resend API if API Key present
    if resend_key:
        try:
            url = "https://api.resend.com/emails"
            payload = {
                "from": sender_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": plain_content
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 201):
                    print(f"[EMAIL SERVICE] OTP email delivered to {to_email} via Resend API.")
                    return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else str(e)
            print(f"[EMAIL SERVICE ERROR] Resend API HTTP {e.code} failure: {err_body}")
        except Exception as e:
            print(f"[EMAIL SERVICE ERROR] Resend delivery failed: {e}")

    # 2. Try Standard SMTP if SMTP_HOST present
    if smtp_host:
        try:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USERNAME")
            smtp_pass = os.getenv("SMTP_PASSWORD")

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = to_email
            msg.set_content(plain_content)
            msg.add_alternative(html_content, subtype="html")

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                print(f"[EMAIL SERVICE] OTP email delivered to {to_email} via SMTP.")
                return True
        except (socket.timeout, TimeoutError) as e:
            print(f"[EMAIL SERVICE ERROR] SMTP connection to {smtp_host}:{smtp_port} timed out after 10s: {e}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL SERVICE ERROR] SMTP authentication failed for user '{smtp_user}' on {smtp_host}: {e.smtp_code} {e.smtp_error}")
        except smtplib.SMTPException as e:
            print(f"[EMAIL SERVICE ERROR] SMTP protocol exception on {smtp_host}: {e}")
        except Exception as e:
            print(f"[EMAIL SERVICE ERROR] SMTP delivery failed: {e}")

    # 3. Explicit Development Mode Fallback ONLY
    if is_dev:
        print(f"[EMAIL SERVICE DEV] Verification code for {to_email}: {otp}")
        return True
    
    print(f"[EMAIL SERVICE ERROR] Email delivery failed or provider unconfigured for {to_email} in production environment!")
    return False

