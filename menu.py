import os
import sys
import subprocess

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("\n" + "=" * 50)
    print("       AI-Powered Lead Generation & Outreach       ")
    print("=" * 50)

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        print_header()
        print("\nChoose an option:\n")
        print("1. Website Analysis & Lead Generation (Standard)")
        print("2. Custom Lead Generation Tool")
        print("3. Email Testing Tool")
        print("4. Import Leads from CSV")
        print("5. Check Environment Setup")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            clear_screen()
            print("\nLaunching standard lead generation tool...\n")
            subprocess.run([sys.executable, "app.py"])
            input("\nPress Enter to return to the main menu...")
        
        elif choice == '2':
            clear_screen()
            print("\nLaunching custom lead generation tool...\n")
            subprocess.run([sys.executable, "custom_lead_gen.py"])
            input("\nPress Enter to return to the main menu...")
        
        elif choice == '3':
            clear_screen()
            print("\nLaunching email testing tool...\n")
            subprocess.run([sys.executable, "test_email.py"])
            input("\nPress Enter to return to the main menu...")
        
        elif choice == '4':
            clear_screen()
            print("\nLaunching import leads tool...\n")
            subprocess.run([sys.executable, "import_leads.py"])
            input("\nPress Enter to return to the main menu...")
        
        elif choice == '5':
            check_environment()
            input("\nPress Enter to return to the main menu...")
        
        elif choice == '6':
            print("\nExiting. Thank you for using the AI Lead Generation & Outreach tool!")
            sys.exit(0)
        
        else:
            input("\nInvalid choice. Press Enter to try again...")

def check_environment():
    """Check if the environment is properly configured."""
    print_header()
    print("\nChecking Environment Setup...\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python Version: {python_version}")
    
    # Check for .env file
    if os.path.exists(".env"):
        print("✅ .env file found")
        
        # Check for required environment variables
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_PASSWORD")
        
        if openai_key:
            print(f"✅ OpenAI API Key: {openai_key[:5]}{'*' * 30}")
        else:
            print("❌ OpenAI API Key not found in .env file")
        
        if gmail_user:
            print(f"✅ Gmail User: {gmail_user}")
        else:
            print("❌ Gmail User not found in .env file")
        
        if gmail_password:
            print("✅ Gmail Password: [CONFIGURED]")
        else:
            print("❌ Gmail Password not found in .env file")
    else:
        print("❌ .env file not found")
        print("Please create a .env file with the following variables:")
        print("OPENAI_API_KEY=your_openai_api_key")
        print("GMAIL_USER=your_gmail_email")
        print("GMAIL_PASSWORD=your_gmail_app_password")
    
    # Check required directories
    if not os.path.exists("output"):
        print("Creating 'output' directory...")
        os.makedirs("output")
        print("✅ 'output' directory created")
    else:
        print("✅ 'output' directory exists")
    
    # Try importing required packages
    required_packages = [
        "openai", "requests", "beautifulsoup4", "playwright", 
        "python-dotenv", "csv", "json"
    ]
    
    print("\nChecking required packages:")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing packages. Install them using:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("\nAll required packages are installed!")
    
    # Check if Playwright browsers are installed
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
        print("✅ Playwright browsers installed")
    except Exception as e:
        print(f"❌ Playwright browsers not installed properly: {e}")
        print("Run 'playwright install' to install browsers")

if __name__ == "__main__":
    main_menu() 