import json
import openai
import random
from config import OPENAI_API_KEY
from utils.industry_matcher import identify_industry, get_industry_leads, enhance_lead_generation, INDUSTRY_MAPPING

openai.api_key = OPENAI_API_KEY

# Dictionary of fallback leads for common business types
FALLBACK_LEADS = {
    "fashion": [
        {
            "name": "Emma Johnson",
            "email": "emmaj@fashionstudio.com",
            "description": "Owner of a boutique fashion studio specializing in custom designs",
            "relevance": "Looking to expand reach and connect with more clients through digital platforms"
        },
        {
            "name": "Michael Chen",
            "email": "mchen@elitedesigns.com",
            "description": "Lead designer at Elite Designs, a premium clothing label",
            "relevance": "Interested in technology platforms that can showcase designs to a broader audience"
        },
        {
            "name": "Sophia Rodriguez",
            "email": "sophia@tailormade.co",
            "description": "Master tailor with 15 years of experience in bespoke clothing",
            "relevance": "Seeking to expand client base beyond local market"
        }
    ],
    "tech": [
        {
            "name": "David Park",
            "email": "dpark@innovatetech.com",
            "description": "CTO of InnovateTech, focusing on AI integration for businesses",
            "relevance": "Looking for new technology partnerships to expand service offerings"
        },
        {
            "name": "Sarah Wilson",
            "email": "swilson@techsolutions.io",
            "description": "Founder of TechSolutions, a software development company",
            "relevance": "Interested in AI tools that can enhance their existing applications"
        },
        {
            "name": "James Thompson",
            "email": "jthompson@digitaledge.net",
            "description": "Product Manager at Digital Edge, specializing in consumer applications",
            "relevance": "Seeking technology partners to improve product capabilities"
        }
    ],
    "general": [
        {
            "name": "Robert Garcia",
            "email": "rgarcia@businessgrowth.com",
            "description": "Business development consultant for small to medium businesses",
            "relevance": "Helps clients find innovative solutions to grow their customer base"
        },
        {
            "name": "Lisa Patel",
            "email": "lpatel@marketingpro.com",
            "description": "Marketing Director specializing in digital strategy",
            "relevance": "Always looking for new platforms to recommend to clients"
        },
        {
            "name": "John Williams",
            "email": "jwilliams@nextstepbusiness.com",
            "description": "Entrepreneur and angel investor in technology startups",
            "relevance": "Interested in innovative business models and technology applications"
        }
    ]
}

def generate_leads(business_analysis):
    """
    Generate synthetic leads based on business analysis
    Input: Business analysis JSON string or dict
    Output: List of potential leads with name, email, and relevance
    """
    # Parse analysis if it's a string
    if isinstance(business_analysis, str):
        try:
            analysis = json.loads(business_analysis)
        except Exception as e:
            print(f"Error parsing analysis JSON: {e}")
            # If we can't parse, try checking for lofai in the string
            if "lofai" in business_analysis.lower() or "fashion" in business_analysis.lower():
                print("Using fashion fallback leads")
                return FALLBACK_LEADS["fashion"]
            elif "tech" in business_analysis.lower() or "software" in business_analysis.lower() or "ai" in business_analysis.lower():
                print("Using tech fallback leads")
                return FALLBACK_LEADS["tech"]
            else:
                print("Using general fallback leads")
                return FALLBACK_LEADS["general"]
    else:
        analysis = business_analysis
    
    # If this is empty or not a dictionary, use fallbacks
    if not analysis or not isinstance(analysis, dict):
        print("Invalid analysis data, using general fallback leads")
        return FALLBACK_LEADS["general"]
    
    # Step 1: Try our industry-specific lead generation first
    # This is more accurate for specific industries and doesn't require API calls
    try:
        if 'business_data' in analysis:
            # If we have business_data, use enhance_lead_generation which combines industry and analysis data
            business_data = analysis['business_data']
            leads = enhance_lead_generation(business_data, analysis, count=3)
            if leads:
                print("Generated industry-specific leads based on business type")
                return leads
    except Exception as e:
        print(f"Error in industry-specific lead generation: {e}")
    
    # Step 2: Check if we have a business_type to work with
    business_type = analysis.get("business_type", "").lower() if isinstance(analysis, dict) else ""
    
    # Use fallbacks if we have insufficient information
    if (not business_type or "unknown" in business_type or "insufficient" in business_type) and isinstance(analysis, dict):
        # Look for "lofai" or fashion/tech keywords in any part of the analysis
        analysis_str = str(analysis).lower()
        if "lofai" in analysis_str or "fashion" in analysis_str or "clothing" in analysis_str or "tailor" in analysis_str:
            print("Using fashion fallback leads based on keywords")
            return FALLBACK_LEADS["fashion"]
        elif "tech" in analysis_str or "software" in analysis_str or "ai" in analysis_str or "digital" in analysis_str:
            print("Using tech fallback leads based on keywords")
            return FALLBACK_LEADS["tech"]
        else:
            print("Using general fallback leads - no clear business type")
            return FALLBACK_LEADS["general"]
    
    # Step 3: If we get here, try OpenAI API to generate leads
    # Create prompt for lead generation
    lead_types = ", ".join(analysis.get("lead_type", [])) if isinstance(analysis.get("lead_type"), list) else analysis.get("lead_type", "")
    
    if not lead_types or "unknown" in lead_types.lower() or "insufficient" in lead_types.lower():
        # Special case for LOFAI
        if "lofai" in str(analysis).lower():
            lead_types = "Fashion Designers, Tailors, Clothing Manufacturers"
        else:
            # Try to infer lead types from business type
            business_type_str = str(business_type).lower()
            if "fashion" in business_type_str or "clothing" in business_type_str or "apparel" in business_type_str:
                lead_types = "Fashion Designers, Tailors, Clothing Brands"
            elif "tech" in business_type_str or "software" in business_type_str or "ai" in business_type_str:
                lead_types = "Technology Companies, Software Developers, AI Specialists"
            elif "ecommerce" in business_type_str or "retail" in business_type_str or "shop" in business_type_str:
                lead_types = "Product Suppliers, Brand Owners, Manufacturers"
            else:
                lead_types = "Business Owners, Service Providers"
    
    prompt = f"""
    Generate 3 synthetic leads (potential partners/customers) for a {analysis.get("business_type", "business")} 
    that needs to connect with {lead_types}.
    
    For each lead, provide:
    1. A realistic full name
    2. A professional email address
    3. A brief description of their business/profile (specific to their industry)
    4. Why they'd be interested in this partnership (specific value they would get)
    
    Format as JSON: {{
        "leads": [
            {{
                "name": "Full Name",
                "email": "email@domain.com",
                "description": "Brief description",
                "relevance": "Why they'd be interested"
            }}
        ]
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        
        try:
            parsed = json.loads(result)
            return parsed["leads"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing leads response: {e}")
            
            # Try to extract the JSON with regex
            import re
            json_match = re.search(r'(\{.*"leads":\s*\[.*\].*\})', result.replace('\n', ' '), re.DOTALL)
            if json_match:
                try:
                    matched_json = json_match.group(1)
                    parsed = json.loads(matched_json)
                    if "leads" in parsed:
                        return parsed["leads"]
                except:
                    pass
            
            # Special case for LOFAI
            if "lofai" in str(analysis).lower():
                return FALLBACK_LEADS["fashion"]
            
            # Fallback based on keywords in the business type
            if isinstance(analysis, dict) and "business_type" in analysis:
                business_type = analysis["business_type"].lower()
                if "fashion" in business_type or "clothing" in business_type or "apparel" in business_type:
                    return FALLBACK_LEADS["fashion"]
                elif "tech" in business_type or "software" in business_type or "ai" in business_type:
                    return FALLBACK_LEADS["tech"]
            
            # Default fallback
            return FALLBACK_LEADS["general"]
            
    except Exception as e:
        print(f"Error generating leads: {e}")
        
        # Special case for LOFAI
        if isinstance(analysis, dict) and "business_type" in analysis:
            business_type = analysis["business_type"].lower()
            if "fashion" in business_type or "clothing" in business_type or "apparel" in business_type or "lofai" in str(analysis).lower():
                return FALLBACK_LEADS["fashion"]
            elif "tech" in business_type or "software" in business_type or "ai" in business_type:
                return FALLBACK_LEADS["tech"]
        
        # Final fallback
        return FALLBACK_LEADS["general"]

def generate_email_content(business_data, lead_info):
    """
    Generate personalized email content for a specific lead
    """
    # Get business name and add a fallback
    business_name = business_data.get('business_name', 'our company')
    
    # Special case for LOFAI
    is_lofai = "lofai" in business_name.lower()
    
    # Extract business_type from structured data if available
    business_type = ""
    value_prop = ""
    
    if 'structured_data' in business_data and isinstance(business_data['structured_data'], str):
        try:
            structured = json.loads(business_data['structured_data'])
            business_type = structured.get('business_type', '')
            value_prop = structured.get('value_proposition', '')
        except:
            pass
    
    # Add LOFAI-specific context if needed
    lofai_context = ""
    if is_lofai:
        lofai_context = "LOFAI is a fashion-tech platform that connects tailors and fashion designers with potential clients using AI technology."
        
        # If lead is fashion-related, add specific value proposition
        lead_desc = lead_info.get('description', '').lower()
        if any(word in lead_desc for word in ['tailor', 'fashion', 'design', 'clothing', 'apparel']):
            lofai_context += " Our platform helps fashion professionals like you reach more clients and grow your business through our AI-powered matching system."
    
    # Identify industry for specialized email templates
    try:
        industry, _ = identify_industry(business_data)
        
        # Get industry-specific value propositions
        industry_data = INDUSTRY_MAPPING.get(industry, {})
        industry_value_props = industry_data.get('value_props', [])
        
        if industry_value_props and not value_prop:
            value_prop = random.choice(industry_value_props)
    except:
        industry = ""
    
    prompt = f"""
    Write a personalized cold outreach email:
    
    FROM: A representative of {business_name}
    TO: {lead_info['name']}, who is {lead_info['description']}
    
    {lofai_context}
    
    Business type: {business_type}
    Value proposition: {value_prop}
    Industry: {industry}
    
    The email should:
    1. Be brief (max 150 words)
    2. Mention why {lead_info['name']} specifically would benefit from this partnership
    3. Include a clear call-to-action
    4. Be professional but conversational in tone
    5. Reference specific aspects of the recipient's business in relation to our offering
    
    Key information about the recipient: {lead_info['relevance']}
    
    Format response as plain text email only, no explanation, include a professional signature.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating email content: {e}")
        
        # Fallback email template
        if is_lofai:
            return f"""
Subject: Partnership Opportunity with LOFAI

Dear {lead_info['name']},

I hope this email finds you well. I am reaching out on behalf of LOFAI, a fashion-tech platform that connects talented fashion professionals like yourself with potential clients.

Given your background in {lead_info['description'].split(',')[0]}, we believe our AI-powered platform could help you {lead_info['relevance'].lower() if lead_info['relevance'].endswith('.') else lead_info['relevance'].lower() + '.'}

Would you be available for a brief 15-minute call next week to discuss how LOFAI can help grow your business?

Looking forward to hearing from you.

Best regards,
Marketing Team
LOFAI
www.lofai.ng
            """
        else:
            return f"""
Subject: Partnership Opportunity with {business_name}

Dear {lead_info['name']},

I hope this email finds you well. I am reaching out because we believe there's a great opportunity for collaboration between {business_name} and your business.

Given your experience as {lead_info['description'].split(',')[0]}, we think our services could help you achieve your goals and address your needs.

Would you be available for a quick call next week to explore potential synergies?

Looking forward to your response.

Best regards,
Marketing Team
{business_name}
            """
