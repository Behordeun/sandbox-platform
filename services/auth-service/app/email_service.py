import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email with HTML content"""
        if not self.smtp_username or not self.smtp_password:
            print(f"Email would be sent to {to_email}: {subject}")
            return True  # Mock success for development

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

    def send_registration_confirmation(self, to_email: str, first_name: str) -> bool:
        """Send registration confirmation email"""
        subject = "Welcome to DPI Sandbox Platform! 🇳🇬"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1>🇳🇬 Welcome to DPI Sandbox!</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>Hello {first_name}!</h2>
                
                <p>Your account has been successfully created on the DPI Sandbox Platform.</p>
                
                <p>You can now access Nigerian Digital Public Infrastructure services:</p>
                <ul>
                    <li>🆔 NIN Verification</li>
                    <li>🏦 BVN Verification</li>
                    <li>📱 SMS Services</li>
                    <li>🤖 AI Services</li>
                </ul>
                
                <div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Get Started:</strong><br>
                    API Gateway: <a href="http://localhost:8080/docs">http://localhost:8080/docs</a><br>
                    API Guide: <a href="http://localhost:8080/api/v1/examples/nin">View Examples</a>
                </div>
                
                <p>Happy coding!</p>
                <p><strong>The DPI Sandbox Team</strong></p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email with verification link"""
        subject = "Reset Your DPI Sandbox Password"

        reset_link = (
            f"http://localhost:3000/reset-password?token={reset_token}&email={to_email}"
        )

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1>🔐 Password Reset Request</h1>
            </div>
            
            <div style="padding: 20px;">
                <h2>Reset Your Password</h2>
                
                <p>You requested to reset your password for your DPI Sandbox account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background: #3498db; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy and paste this link in your browser:</p>
                <p style="background: #f8f9fa; padding: 10px; border-radius: 3px; word-break: break-all;">
                    {reset_link}
                </p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Security Note:</strong><br>
                    This link will expire in 30 minutes. If you didn't request this reset, please ignore this email.
                </div>
                
                <p><strong>The DPI Sandbox Team</strong></p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)


# Global email service instance
email_service = EmailService()
