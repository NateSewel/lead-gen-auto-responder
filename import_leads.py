import csv
import json
import os
import time
from utils.lead_finder import generate_email_content
from utils.email_handler import send_email

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("\n=== Import Leads Tool ===\n")
    print("This tool lets you import leads from a CSV file and generate personalized emails\n")
    
    # Ensure output directory exists
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # First, check if a sample CSV exists, if not create one
    sample_path = "output/sample_leads.csv"
    if not os.path.exists(sample_path):
        create_sample = input("Would you like to create a sample CSV file as a template? (y/n): ").lower()
        if create_sample == 'y':
            with open(sample_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['name', 'email', 'description', 'relevance'])
                writer.writerow(['John Doe', 'john@example.com', 'Fashion Designer at StyleHouse', 'Looking to expand client base'])
                writer.writerow(['Jane Smith', 'jane@example.com', 'Owner of TailorMade Boutique', 'Interested in technology platforms'])
                writer.writerow(['Alex Wong', 'alex@example.com', 'Master Tailor with 10 years experience', 'Wants to reach more customers'])
            print(f"\n✅ Sample CSV created at {sample_path}")
    
    # Get CSV file path
    while True:
        csv_path = input("\nEnter path to your CSV file (or press Enter to use sample): ").strip()
        
        if not csv_path and os.path.exists(sample_path):
            csv_path = sample_path
            print(f"Using sample CSV: {sample_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            if input("Try again? (y/n): ").lower() != 'y':
                return
        else:
            break
    
    # Read the CSV file
    leads = []
    try:
        with open(csv_path, 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Assume first row is headers
            
            # Check required columns
            required_cols = ['name', 'email', 'description', 'relevance']
            missing_cols = [col for col in required_cols if col.lower() not in [h.lower() for h in headers]]
            
            if missing_cols:
                print(f"❌ CSV is missing required columns: {', '.join(missing_cols)}")
                print("CSV must have columns: name, email, description, relevance")
                return
            
            # Map column indices
            name_idx = headers.index('name') if 'name' in headers else headers.index('Name')
            email_idx = headers.index('email') if 'email' in headers else headers.index('Email')
            desc_idx = next((i for i, h in enumerate(headers) if h.lower() in ['description', 'desc']), None)
            rel_idx = next((i for i, h in enumerate(headers) if h.lower() in ['relevance', 'rel']), None)
            
            # Read leads
            for row in reader:
                if not row or not row[email_idx]:  # Skip empty rows or rows without email
                    continue
                    
                leads.append({
                    'name': row[name_idx],
                    'email': row[email_idx],
                    'description': row[desc_idx] if desc_idx is not None and desc_idx < len(row) else '',
                    'relevance': row[rel_idx] if rel_idx is not None and rel_idx < len(row) else ''
                })
        
        print(f"✅ Successfully imported {len(leads)} leads")
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return
    
    # If no leads were imported
    if not leads:
        print("❌ No valid leads found in the CSV file")
        return
    
    # Save imported leads to JSON
    with open("output/imported_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    
    # Get business information for email generation
    print("\n=== Business Information ===\n")
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
    
    # Generate emails for each lead
    print("\n📧 Generating personalized emails...")
    
    for i, lead in enumerate(leads):
        print(f"\nEmail for Lead {i+1}: {lead['name']} ({lead['email']})")
        email_content = generate_email_content(business_data, lead)
        
        # Save email to file
        with open(f"output/imported_email_{i+1}.txt", "w") as f:
            f.write(f"To: {lead['email']}\n")
            f.write(f"Subject: Partnership Opportunity with {business_data['business_name']}\n\n")
            f.write(email_content)
        
        print(f"✅ Email saved to output/imported_email_{i+1}.txt")
        
        # Ask if user wants to preview the email
        preview = input("\nPreview this email? (y/n): ").lower()
        if preview == 'y':
            print("\n=== Email Preview ===\n")
            print(f"To: {lead['email']}")
            print(f"Subject: Partnership Opportunity with {business_data['business_name']}")
            print(f"\n{email_content}")
        
        # Ask if user wants to modify this email
        modify_email = input("\nModify this email? (y/n): ").lower()
        if modify_email == 'y':
            new_content = ""
            print("\nEnter new email content (type 'END' on a new line when finished):")
            while True:
                line = input()
                if line == 'END':
                    break
                new_content += line + "\n"
            
            # Save modified email
            with open(f"output/imported_email_{i+1}.txt", "w") as f:
                f.write(f"To: {lead['email']}\n")
                f.write(f"Subject: Partnership Opportunity with {business_data['business_name']}\n\n")
                f.write(new_content)
            
            email_content = new_content
            print(f"✅ Email updated and saved")
        
        # Ask if user wants to send this email
        send_option = input("\nSend this email? (y/n): ").lower()
        if send_option == 'y':
            try:
                send_email(
                    lead['email'],
                    f"Partnership Opportunity with {business_data['business_name']}",
                    email_content
                )
                print(f"✅ Email sent to {lead['email']}")
                time.sleep(1)  # Sleep to avoid rate limiting
            except Exception as e:
                print(f"❌ Error sending email: {e}")
                print("\nPlease make sure your .env file contains valid GMAIL_USER and GMAIL_PASSWORD.")
                print("Note: For Gmail, you need to use an App Password. See https://support.google.com/accounts/answer/185833")
                
            # After first email, ask if user wants to continue or batch send
            if i == 0 and len(leads) > 1:
                continue_option = input("\nHow would you like to proceed?\n1. Continue sending one by one\n2. Send all remaining emails automatically\n3. Stop sending\n\nSelect option (1/2/3): ")
                
                if continue_option == '3':
                    print("\n✅ Email sending stopped. All emails are saved to the output directory.")
                    break
                elif continue_option == '2':
                    # Batch send remaining emails
                    print(f"\nSending remaining {len(leads) - (i+1)} emails...")
                    for j in range(i+1, len(leads)):
                        try:
                            lead_j = leads[j]
                            email_j = generate_email_content(business_data, lead_j)
                            
                            # Save email
                            with open(f"output/imported_email_{j+1}.txt", "w") as f:
                                f.write(f"To: {lead_j['email']}\n")
                                f.write(f"Subject: Partnership Opportunity with {business_data['business_name']}\n\n")
                                f.write(email_j)
                            
                            # Send email
                            send_email(
                                lead_j['email'],
                                f"Partnership Opportunity with {business_data['business_name']}",
                                email_j
                            )
                            print(f"✅ Email sent to {lead_j['email']}")
                            time.sleep(2)  # Longer sleep for batch sending
                        except Exception as e:
                            print(f"❌ Error processing lead {j+1}: {e}")
                    
                    print("\n✅ Batch email sending completed.")
                    break
    
    print("\n🎉 Import leads and email drafting completed!")
    print(f"📁 All emails saved to the 'output' directory")

if __name__ == "__main__":
    main() 