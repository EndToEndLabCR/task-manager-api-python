import logging
import os

import resend

logger = logging.getLogger(__name__)


class ResendEmailSender:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY")
        self._from_address = os.getenv("RESEND_FROM_EMAIL", "noreply@yourdomain.com")
        self._frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    async def send_password_reset(self, to_email: str, reset_token: str) -> None:
        reset_url = f"{self._frontend_url}/reset-password?token={reset_token}"

        params: resend.Emails.SendParams = {
            "from": self._from_address,
            "to": [to_email],
            "subject": "Reset your password",
            "html": self._reset_password_template(reset_url),
        }

        try:
            resend.Emails.send(params)
            logger.info(f"Password reset email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            raise

    async def send_verification_email(self, to_email: str, verification_token: str) -> None:
        verify_url = f"{self._frontend_url}/verify-email?token={verification_token}"

        params: resend.Emails.SendParams = {
            "from": self._from_address,
            "to": [to_email],
            "subject": "Verify your email address",
            "html": self._verification_email_template(verify_url),
        }

        try:
            resend.Emails.send(params)
            logger.info(f"Verification email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            raise

    @staticmethod
    def _reset_password_template(reset_url: str) -> str:
        return f"""
        <html>
          <body style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 32px;">
            <h2>Reset your password</h2>
            <p>Click the button below to reset your password. This link expires in <strong>1 hour</strong>.</p>
            <a href="{reset_url}"
               style="display: inline-block; padding: 12px 24px; background: #01696f;
                      color: white; text-decoration: none; border-radius: 6px; margin: 16px 0;">
              Reset password
            </a>
            <p style="color: #7a7974; font-size: 14px;">
              If you didn't request this, you can safely ignore this email.
            </p>
          </body>
        </html>
        """

    @staticmethod
    def _verification_email_template(verify_url: str) -> str:
        return f"""
        <html>
          <body style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 32px;">
            <h2>Verify your email</h2>
            <p>Click the button below to verify your email address. This link expires in <strong>24 hours</strong>.</p>
            <a href="{verify_url}"
               style="display: inline-block; padding: 12px 24px; background: #01696f;
                      color: white; text-decoration: none; border-radius: 6px; margin: 16px 0;">
              Verify email
            </a>
            <p style="color: #7a7974; font-size: 14px;">
              If you didn't create an account, you can safely ignore this email.
            </p>
          </body>
        </html>
        """
