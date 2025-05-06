from utils.email_handler import send_email
from utils.lead_finder import generate_email_content
import json
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("\n=== Email Testing Tool ===\n")
    print("This tool lets you test email generation and sending with your own lead data\n")
    
    # Get business information
    business_name = input("Enter your business name: ").strip()
    business_type = input("Enter your business type (e.g., fashion-tech platform): ").strip()
    business_value = input("Enter your business value proposition: ").strip()
    
    business_data = {
        "business_name": business_name,
        "description": business_type,
        "structured_data": json.dumps({
            "business_name": business_name,
            "business_type": business_type,
            "value_proposition": business_value
        })
    }
    
    # Ask to create new lead or use existing
    print("\n=== Lead Information ===\n")
    print("1. Enter your own lead")
    print("2. Use a sample lead for testing")
    choice = input("\nSelect an option (1 or 2): ").strip()
    
    if choice == "1":
        # Get lead information
        lead_name = input("\nEnter lead name: ").strip()
        lead_email = input("Enter lead email: ").strip()
        lead_description = input("Enter lead description (e.g., Fashion Designer at XYZ): ").strip()
        lead_relevance = input("Enter why this lead would be interested in your business: ").strip()
        
        lead_info = {
            "name": lead_name,
            "email": lead_email,
            "description": lead_description,
            "relevance": lead_relevance
        }
    else:
        # Use sample data based on business type
        print("\nUsing sample lead data for testing...")
        
        if "fashion" in business_type.lower() or "clothing" in business_type.lower() or "tailor" in business_type.lower():
            lead_info = {
                "name": "Emma Johnson",
                "email": "your_test_email@example.com",  # User needs to replace this
                "description": "Owner of a boutique fashion studio specializing in custom designs",
                "relevance": "Looking to expand reach and connect with more clients through digital platforms"
            }
        elif "tech" in business_type.lower() or "software" in business_type.lower() or "ai" in business_type.lower():
            lead_info = {
                "name": "David Park",
                "email": "your_test_email@example.com",  # User needs to replace this
                "description": "CTO of InnovateTech, focusing on AI integration for businesses",
                "relevance": "Looking for new technology partnerships to expand service offerings"
            }
        else:
            lead_info = {
                "name": "John Williams",
                "email": "your_test_email@example.com",  # User needs to replace this
                "description": "Entrepreneur and angel investor in technology startups",
                "relevance": "Interested in innovative business models and technology applications"
            }
        
        # Update the email
        lead_info["email"] = input(f"\nEnter your test email address to receive the email for {lead_info['name']}: ").strip()
    
    # Generate email
    print("\nGenerating personalized email content...")
    email_content = generate_email_content(business_data, lead_info)
    
    # Save email to file
    if not os.path.exists("output"):
        os.makedirs("output")
    
    with open("output/test_email.txt", "w") as f:
        f.write(f"To: {lead_info['email']}\n")
        f.write(f"Subject: Partnership Opportunity with {business_data['business_name']}\n\n")
        f.write(email_content)
    
    print(f"\nEmail preview saved to output/test_email.txt")
    
    # Show preview
    print("\n=== Email Preview ===\n")
    print(f"To: {lead_info['email']}")
    print(f"Subject: Partnership Opportunity with {business_data['business_name']}")
    print(f"\n{email_content}")
    
    # Ask to send
    send_option = input("\nSend this email? (y/n): ").lower()
    if send_option == 'y':
        try:
            send_email(
                lead_info['email'],
                f"Partnership Opportunity with {business_data['business_name']}",
                email_content
            )
            print(f"\n✅ Email sent to {lead_info['email']}")
        except Exception as e:
            print(f"\n❌ Error sending email: {e}")
            print("\nPlease make sure your .env file contains valid GMAIL_USER and GMAIL_PASSWORD.")
            print("Note: For Gmail, you need to use an App Password. See https://support.google.com/accounts/answer/185833")
    else:
        print("\nEmail sending canceled.")

if __name__ == "__main__":
    main() 