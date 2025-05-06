from utils.scraper import scrape_static, scrape_dynamic, extract_structured_data
from utils.analyzer import analyze_business
from utils.lead_finder import generate_leads, generate_email_content
from utils.email_handler import send_email
import json
import os
import time

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("\n=== Custom Lead Generation Tool ===\n")
    
    # Step 1: Get website URL or use manual data entry
    print("1. Analyze a website URL")
    print("2. Manually enter business information")
    option = input("\nSelect an option (1 or 2): ").strip()
    
    if option == "1":
        # Process website
        url = input("\nEnter target website URL: ").strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print(f"\nAnalyzing website: {url}")
        print("This may take a minute...\n")
        
        # Scrape website data
        print("🔍 Scraping website...")
        scraped_data = scrape_static(url)
        
        if not scraped_data:
            print("Static scraping failed. Trying dynamic...")
            scraped_data = scrape_dynamic(url)
        
        if not scraped_data:
            print("All scraping attempts failed.")
            return
        
        print(f"✅ Successfully scraped: {scraped_data['business_name']}")
        
        # Extract structured data using LLM
        print("\n🔄 Extracting business information...")
        structured_data = extract_structured_data(scraped_data)
        
        # Add structured data to the scraped data
        if structured_data:
            scraped_data['structured_data'] = structured_data
            print("✅ Extracted structured business information")
            
            # Let's see if we can parse it and show it
            try:
                parsed = json.loads(structured_data)
                print(f"\nBusiness Type: {parsed.get('business_type', 'Unknown')}")
                if 'target_audience' in parsed:
                    print(f"Target Audience: {parsed.get('target_audience', 'Unknown')}")
                if 'services' in parsed:
                    services = parsed.get('services', [])
                    if isinstance(services, list):
                        print(f"Services: {', '.join(services[:3])}")
                    else:
                        print(f"Services: {services}")
            except:
                pass
        
        # Analyze business
        print("\n🧠 Analyzing business model and potential leads...")
        analysis_json = analyze_business(scraped_data)
        
        try:
            analysis = json.loads(analysis_json)
            print(f"✅ Business Type: {analysis.get('business_type', 'Unknown')}")
            print(f"✅ Identified Lead Types: {', '.join(analysis.get('lead_type', ['Unknown']))}")
        except:
            print("⚠️ Error parsing analysis JSON.")
            analysis = analysis_json
    else:
        # Manual data entry
        print("\n=== Manual Business Information Entry ===\n")
        business_name = input("Enter business name: ").strip()
        business_type = input("Enter business type (e.g., fashion-tech platform): ").strip()
        
        # Additional information
        target_audience = input("Enter target audience (e.g., fashion designers, tailors): ").strip()
        services = input("Enter services offered (comma separated): ").strip()
        value_prop = input("Enter value proposition: ").strip()
        
        # Create scraped_data structure
        scraped_data = {
            "business_name": business_name,
            "description": business_type,
            "main_content": f"Business providing {services} to {target_audience}. {value_prop}",
            "structured_data": json.dumps({
                "business_name": business_name,
                "business_type": business_type,
                "target_audience": target_audience,
                "services": services.split(","),
                "value_proposition": value_prop
            })
        }
        
        # Create analysis structure
        analysis = {
            "business_type": business_type,
            "lead_type": target_audience.split(","),
            "lead_search_keywords": [kw.strip() for kw in target_audience.split(",")],
            "value_proposition_highlights": value_prop
        }
        
        print(f"\n✅ Manual business information processed")
    
    # Generate leads
    print("\n👥 Generating potential leads...")
    leads = generate_leads(analysis)
    
    if not leads:
        print("❌ Failed to generate leads. Exiting.")
        return
    
    print(f"✅ Generated {len(leads)} potential leads")
    
    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Save leads to file
    with open("output/custom_leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    
    print(f"\nLeads saved to output/custom_leads.json")
    
    # Ask if user wants to customize leads
    customize = input("\nDo you want to customize the generated leads? (y/n): ").lower()
    
    if customize == 'y':
        # Show current leads
        for i, lead in enumerate(leads):
            print(f"\nLead {i+1}:")
            print(f"Name: {lead['name']}")
            print(f"Email: {lead['email']}")
            print(f"Description: {lead['description']}")
            print(f"Relevance: {lead['relevance']}")
            
            # Ask if user wants to modify this lead
            modify = input(f"\nModify lead {i+1}? (y/n): ").lower()
            if modify == 'y':
                leads[i]['name'] = input(f"Enter new name [{lead['name']}]: ").strip() or lead['name']
                leads[i]['email'] = input(f"Enter new email [{lead['email']}]: ").strip() or lead['email']
                leads[i]['description'] = input(f"Enter new description [{lead['description']}]: ").strip() or lead['description']
                leads[i]['relevance'] = input(f"Enter new relevance [{lead['relevance']}]: ").strip() or lead['relevance']
                print(f"✅ Lead {i+1} updated")
        
        # Save updated leads
        with open("output/custom_leads.json", "w") as f:
            json.dump(leads, f, indent=2)
        
        print(f"\n✅ Updated leads saved to output/custom_leads.json")
    
    # Generate and save emails
    print("\n📧 Generating personalized emails...")
    
    for i, lead in enumerate(leads):
        print(f"\nEmail for Lead {i+1}: {lead['name']} ({lead['email']})")
        email_content = generate_email_content(scraped_data, lead)
        
        # Save email to file
        with open(f"output/custom_email_{i+1}.txt", "w") as f:
            f.write(f"To: {lead['email']}\n")
            f.write(f"Subject: Partnership Opportunity with {scraped_data['business_name']}\n\n")
            f.write(email_content)
        
        print(f"✅ Email saved to output/custom_email_{i+1}.txt")
        
        # Ask if user wants to preview the email
        preview = input("\nPreview this email? (y/n): ").lower()
        if preview == 'y':
            print("\n=== Email Preview ===\n")
            print(f"To: {lead['email']}")
            print(f"Subject: Partnership Opportunity with {scraped_data['business_name']}")
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
            with open(f"output/custom_email_{i+1}.txt", "w") as f:
                f.write(f"To: {lead['email']}\n")
                f.write(f"Subject: Partnership Opportunity with {scraped_data['business_name']}\n\n")
                f.write(new_content)
            
            email_content = new_content
            print(f"✅ Email updated and saved")
        
        # Ask if user wants to send this email
        send_option = input("\nSend this email? (y/n): ").lower()
        if send_option == 'y':
            try:
                send_email(
                    lead['email'],
                    f"Partnership Opportunity with {scraped_data['business_name']}",
                    email_content
                )
                print(f"✅ Email sent to {lead['email']}")
                time.sleep(1)  # Sleep to avoid rate limiting
            except Exception as e:
                print(f"❌ Error sending email: {e}")
                print("\nPlease make sure your .env file contains valid GMAIL_USER and GMAIL_PASSWORD.")
                print("Note: For Gmail, you need to use an App Password. See https://support.google.com/accounts/answer/185833")
    
    print("\n🎉 Custom lead generation and email drafting completed!")
    print(f"📁 All leads and emails saved to the 'output' directory")

if __name__ == "__main__":
    main() 