from config import GMAIL_USER, GMAIL_PASSWORD
import smtplib
from email.mime.text import MIMEText
import sys

def send_email(to_email, subject, body):
    """
    Send an email using Gmail SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body text
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("\n❌ Email configuration error:")
        print("Missing Gmail credentials in .env file")
        print("Make sure you have both GMAIL_USER and GMAIL_PASSWORD set")
        return False
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    
    try:
        # First try with standard port 587
        print("\nConnecting to Gmail SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1)  # Enable debug output
        print("Starting TLS encryption...")
        server.starttls()
        print(f"Attempting login for {GMAIL_USER}...")
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        print("Sending email...")
        server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Error using port 587: {e}")
        print("\nAttempting alternative method...")
        
        try:
            # Try alternate port 465 with SSL
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server_ssl.set_debuglevel(1)  # Enable debug output
            print(f"Attempting login for {GMAIL_USER} using SSL...")
            server_ssl.login(GMAIL_USER, GMAIL_PASSWORD)
            print("Sending email...")
            server_ssl.sendmail(GMAIL_USER, [to_email], msg.as_string())
            server_ssl.quit()
            print("✅ Email sent successfully using SSL!")
            return True
        except Exception as e2:
            print(f"\n❌ Error using SSL port 465: {e2}")
            print("\n✘ Gmail Authentication Error")
            print("-----------------------------")
            print("1. Check that your Gmail account has 'Less secure app access' enabled")
            print("   or preferably use an App Password")
            print("2. Verify the App Password is correctly copied to your .env file")
            print("3. Make sure there are no extra spaces in the password")
            print("4. If using 2FA, you MUST use an App Password")
            print("\nTo generate an App Password:")
            print("1. Go to https://myaccount.google.com/security")
            print("2. Under 'Signing in to Google', select 'App Passwords'")
            print("3. Generate a new App Password for 'Mail' and 'Other'")
            print("4. Copy the 16-character password (with spaces) to your .env file")
            return False