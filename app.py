from utils.scraper import scrape_static, scrape_dynamic, extract_structured_data
from utils.analyzer import analyze_business
from utils.lead_finder import generate_leads, generate_email_content
from utils.email_handler import send_email
from utils.industry_matcher import identify_industry
import json
import time
import os
from config import OPENAI_API_KEY, GMAIL_USER, GMAIL_PASSWORD

print(f"API Key Loaded: {OPENAI_API_KEY[:5] if OPENAI_API_KEY else 'NOT FOUND'}...")
print(f"Gmail User: {GMAIL_USER or 'NOT FOUND'}")
print(f"Gmail Password: {'CONFIGURED' if GMAIL_PASSWORD else 'NOT FOUND'}")

def main():
    """Main function to run the lead generation pipeline"""
    print("\n=== AI Lead Generation & Outreach Agent ===\n")
    
    # Step 1: Get website URL from user
    url = input("\nEnter target website URL: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"\nAnalyzing website: {url}")
    print("This may take a minute...\n")
    
    # Step 2: Scrape website data
    print("🔍 Scraping website...")
    scraped_data = scrape_static(url)
    
    if not scraped_data:
        print("Static scraping failed. Trying dynamic...")
        scraped_data = scrape_dynamic(url)  # Uses Playwright
    
    if not scraped_data:
        print("All scraping attempts failed. Exiting.")
        return
    
    # Print basic info
    print(f"✅ Successfully scraped: {scraped_data['business_name']}")
    
    # Step 3: Use industry matcher for quick industry identification
    try:
        industry, confidence = identify_industry(scraped_data)
        print(f"\n🏢 Industry Identification:")
        print(f"   Industry: {industry.capitalize()}")
        print(f"   Confidence: {confidence:.1f}/10")
    except Exception as e:
        print(f"Industry identification error: {e}")
    
    # Step 4: Extract structured data using LLM
    print("\n🔄 Extracting business information...")
    structured_data = extract_structured_data(scraped_data)
    
    # Add structured data to the scraped data
    if structured_data:
        scraped_data['structured_data'] = structured_data
        print("✅ Extracted structured business information")
    
    # Step 5: Analyze business
    print("\n🧠 Analyzing business model and potential leads...")
    analysis_json = analyze_business(scraped_data)
    
    try:
        analysis = json.loads(analysis_json)
        print(f"✅ Business Type: {analysis.get('business_type', 'Unknown')}")
        print(f"✅ Identified Lead Types: {', '.join(analysis.get('lead_type', ['Unknown']))}")
        
        # Add the original scraped data to the analysis for enhanced lead generation
        analysis['business_data'] = scraped_data
        
    except json.JSONDecodeError:
        print("⚠️ Error parsing analysis JSON. Using raw output.")
        analysis = analysis_json
    
    # Step 6: Generate leads with improved accuracy
    print("\n👥 Generating potential leads...")
    leads = generate_leads(analysis)
    
    if not leads:
        print("❌ Failed to generate leads. Exiting.")
        return
    
    print(f"✅ Generated {len(leads)} potential leads")
    
    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Save leads and emails to file
    with open("output/leads.json", "w") as f:
        json.dump(leads, f, indent=2)
    
    # Step 7: Generate and send personalized emails
    print("\n📧 Generating personalized emails...")
    
    for i, lead in enumerate(leads):
        print(f"\nEmail for Lead {i+1}: {lead['name']} ({lead['email']})")
        email_content = generate_email_content(scraped_data, lead)
        
        # Save email to file
        with open(f"output/email_{i+1}.txt", "w") as f:
            f.write(f"To: {lead['email']}\n")
            f.write(f"Subject: Partnership Opportunity with {scraped_data['business_name']}\n\n")
            f.write(email_content)
        
        print(f"✅ Email saved to output/email_{i+1}.txt")
        
        # Preview the email
        preview_option = input("\nPreview email? (y/n): ").lower()
        if preview_option == 'y':
            print("\n==== Email Preview ====\n")
            print(f"To: {lead['email']}")
            print(f"Subject: Partnership Opportunity with {scraped_data['business_name']}")
            print("")
            print(email_content)
            print("\n==== End Preview ====\n")
        
        # Ask if user wants to send this email
        if GMAIL_USER and GMAIL_PASSWORD:
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
        else:
            print("⚠️ Email sending skipped - Gmail credentials not configured")
    
    print("\n🎉 Lead generation and email drafting completed!")
    print(f"📁 All leads and emails saved to the 'output' directory")

if __name__ == "__main__":
    main()