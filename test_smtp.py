import smtplib
import os
from dotenv import load_dotenv

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def test_gmail_connection():
    """Test Gmail SMTP connection with credentials from .env file"""
    # Load environment variables
    load_dotenv()
    
    # Get email credentials
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    
    clear_screen()
    print("\n=== Gmail SMTP Connection Test ===\n")
    
    # Check if credentials exist
    if not gmail_user or not gmail_password:
        print("❌ Email credentials not found in .env file")
        print("Please ensure your .env file contains:")
        print("GMAIL_USER=your_email@gmail.com")
        print("GMAIL_PASSWORD=your_app_password")
        return False
    
    print(f"Gmail User: {gmail_user}")
    print(f"Password Found: {'Yes' if gmail_password else 'No'}")
    
    if ' ' in gmail_password:
        print("Note: Your password contains spaces (this is normal for App Passwords)")
    
    # Try to connect to Gmail SMTP server
    print("\n1. Testing connection to smtp.gmail.com on port 587 (TLS)...")
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo()
        print("   ✅ Connected to SMTP server")
        
        server.starttls()
        print("   ✅ Started TLS encryption")
        
        # Try to login
        print(f"\n2. Attempting login for {gmail_user}...")
        server.login(gmail_user, gmail_password)
        print("   ✅ Login successful!")
        
        server.quit()
        print("\n✅ Gmail SMTP test passed! Your credentials are working properly.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("\nPossible issues:")
        print("1. Your password may be incorrect")
        print("2. If you're using 2FA, you must use an App Password")
        print("3. Less secure app access might be disabled")
        print("\nTo generate an App Password:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Under 'Signing in to Google', select 'App Passwords'")
        print("3. Generate a new App Password for 'Mail' and 'Other'")
        print("4. Copy the 16-character password (with spaces) to your .env file")
    
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        
        # Try alternate port as a fallback
        print("\nTrying alternate method with SSL on port 465...")
        try:
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            server_ssl.ehlo()
            print("   ✅ Connected to SMTP server using SSL")
            
            print(f"   Attempting login for {gmail_user}...")
            server_ssl.login(gmail_user, gmail_password)
            print("   ✅ Login successful using SSL!")
            
            server_ssl.quit()
            print("\n✅ Gmail SMTP test passed using SSL! Your credentials are working properly.")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ SSL Authentication failed: {e}")
            print("\nPlease check your Gmail credentials and App Password.")
            
        except Exception as e:
            print(f"   ❌ SSL Connection error: {e}")
    
    print("\n❌ Gmail SMTP test failed. Please check your credentials and network connection.")
    return False
    
if __name__ == "__main__":
    test_gmail_connection()
    
    print("\nPress Enter to exit...")
    input() 