"""
Industry-specific lead generation and matching module
This module provides specialized logic for mapping business types to potential lead categories
and generating targeted lead profiles based on industry-specific knowledge.
"""

import json
import re
import random
from typing import Dict, List, Tuple, Any

# Industry mapping: Map business types to potential lead categories and relevant keywords
INDUSTRY_MAPPING = {
    "fashion": {
        "business_types": [
            "fashion platform", "clothing marketplace", "apparel", "fashion tech", 
            "style platform", "clothing brand", "fashion design", "fashion retail"
        ],
        "lead_categories": [
            "Fashion Designers", "Tailors", "Clothing Manufacturers", "Fashion Retailers",
            "Textile Suppliers", "Fashion Influencers", "Boutique Owners"
        ],
        "value_props": [
            "Expand your customer reach through our fashion platform",
            "Connect directly with customers seeking custom clothing",
            "Showcase your designs to a larger audience",
            "Reduce marketing costs while increasing sales"
        ],
        "search_keywords": [
            "fashion designer", "tailor", "bespoke clothing", "custom garments",
            "clothing manufacturer", "fashion retailer", "boutique owner", "textile supplier"
        ]
    },
    "tech": {
        "business_types": [
            "tech platform", "software", "saas", "technology", "app", "digital platform", 
            "ai", "artificial intelligence", "machine learning", "analytics"
        ],
        "lead_categories": [
            "Software Developers", "Tech Startups", "IT Consultants", "Data Scientists",
            "Product Managers", "UX/UI Designers", "Technology Companies"
        ],
        "value_props": [
            "Integrate cutting-edge technology into your business",
            "Enhance your product capabilities with our AI solutions",
            "Scale your technology infrastructure efficiently",
            "Access advanced analytics to drive decision making"
        ],
        "search_keywords": [
            "software developer", "tech startup", "it consultant", "technology company",
            "product manager", "data scientist", "ai specialist", "tech entrepreneur"
        ]
    },
    "ecommerce": {
        "business_types": [
            "ecommerce", "online store", "e-commerce", "online marketplace", "digital store",
            "online retail", "webshop", "online sales"
        ],
        "lead_categories": [
            "Product Suppliers", "Online Retailers", "Dropshippers", "Brand Owners",
            "Logistics Companies", "Marketplace Sellers", "E-commerce Entrepreneurs"
        ],
        "value_props": [
            "Expand your online sales channels",
            "Reach a wider customer base with our platform",
            "Simplify your e-commerce operations",
            "Increase your online visibility and sales"
        ],
        "search_keywords": [
            "online retailer", "product supplier", "e-commerce business", "dropshipper",
            "brand owner", "marketplace seller", "e-commerce entrepreneur"
        ]
    },
    "service": {
        "business_types": [
            "service provider", "consulting", "professional service", "agency", 
            "freelance", "service marketplace", "consulting firm"
        ],
        "lead_categories": [
            "Consultants", "Freelancers", "Service Providers", "Agencies",
            "Professional Service Firms", "Experts", "Specialists"
        ],
        "value_props": [
            "Connect with clients seeking your specific expertise",
            "Expand your service offering through our platform",
            "Find qualified clients more efficiently",
            "Grow your service business with minimal marketing"
        ],
        "search_keywords": [
            "consultant", "freelancer", "service provider", "agency",
            "professional service", "expert", "specialist", "service firm"
        ]
    }
}

# Additional industry categories to be expanded over time
# Add more industries with their specific lead types here

def identify_industry(business_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Identify the primary industry category based on business data
    
    Args:
        business_data: Dictionary containing business information
        
    Returns:
        Tuple with (industry_name, confidence_score)
    """
    # Extract business text to analyze
    business_text = ""
    if isinstance(business_data, dict):
        business_text = (
            business_data.get('business_name', '') + ' ' +
            business_data.get('description', '') + ' ' +
            business_data.get('main_content', '') + ' ' +
            business_data.get('about_content', '')
        ).lower()
        
        # Try to get structured data if available
        if 'structured_data' in business_data:
            try:
                structured = json.loads(business_data['structured_data']) if isinstance(business_data['structured_data'], str) else business_data['structured_data']
                business_text += ' ' + structured.get('business_type', '') + ' ' + structured.get('value_proposition', '')
            except:
                pass
    else:
        # If it's not a dict, try to use it as a string
        business_text = str(business_data).lower()
    
    # Score each industry based on keyword matches
    industry_scores = {}
    
    for industry, data in INDUSTRY_MAPPING.items():
        score = 0
        for keyword in data['business_types']:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', business_text):
                score += 1
                
        # Check for the industry name itself
        if re.search(r'\b' + re.escape(industry.lower()) + r'\b', business_text):
            score += 3  # Higher weight for direct industry mention
                
        # Normalize score based on number of keywords
        if score > 0:
            industry_scores[industry] = score / len(data['business_types']) * 10
    
    # Special case for LOFAI (fashion tech platform)
    if "lofai" in business_text:
        industry_scores["fashion"] = max(industry_scores.get("fashion", 0), 8.5)
        industry_scores["tech"] = max(industry_scores.get("tech", 0), 6.0)
    
    # Get highest scoring industry
    if industry_scores:
        top_industry = max(industry_scores.items(), key=lambda x: x[1])
        return top_industry
    
    # Default to a generic industry with low confidence if no matches
    return ("service", 3.0)

def get_industry_leads(industry: str, count: int = 3) -> List[Dict[str, str]]:
    """
    Generate industry-specific lead profiles
    
    Args:
        industry: Industry name (e.g., "fashion", "tech")
        count: Number of leads to generate
        
    Returns:
        List of lead profiles as dictionaries
    """
    industry_data = INDUSTRY_MAPPING.get(industry, INDUSTRY_MAPPING["service"])
    
    leads = []
    # Get lead categories for this industry
    lead_categories = industry_data["lead_categories"]
    
    # Create realistic names
    first_names = ["Emma", "James", "Sophia", "Michael", "Olivia", "William", "Ava", "John", 
                   "Isabella", "Robert", "Charlotte", "David", "Amelia", "Daniel", "Harper",
                   "Joseph", "Evelyn", "Thomas", "Abigail", "Richard", "Emily", "Charles",
                   "Elizabeth", "Christopher", "Sofia", "Matthew", "Avery", "Anthony", "Ella"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
                  "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"]
    
    # Domain templates for industry-specific email addresses
    domain_templates = {
        "fashion": ["{name}@{biz}design.com", "{name}@{biz}fashion.com", "{name}@{biz}style.co", "{initial}{last}@{biz}fashion.com"],
        "tech": ["{name}@{biz}tech.com", "{name}@{biz}digital.io", "{name}@{biz}solutions.co", "{initial}{last}@{biz}tech.io"],
        "ecommerce": ["{name}@{biz}retail.com", "{name}@{biz}store.com", "{name}@{biz}market.co", "{initial}{last}@{biz}shop.com"],
        "service": ["{name}@{biz}consulting.com", "{name}@{biz}services.com", "{name}@{biz}experts.co", "{initial}{last}@{biz}group.com"]
    }
    
    # Business name components by industry
    business_components = {
        "fashion": ["Style", "Trend", "Stitch", "Fashion", "Thread", "Design", "Apparel", "Mode", "Vogue", "Textile"],
        "tech": ["Tech", "Byte", "Digital", "Smart", "Code", "Cyber", "Data", "Logic", "Cloud", "Pixel"],
        "ecommerce": ["Market", "Store", "Shop", "Commerce", "Retail", "Trade", "Deal", "Buy", "Seller", "Mart"],
        "service": ["Consult", "Advisor", "Expert", "Pro", "Service", "Solution", "Group", "Partner", "Team", "Specialist"]
    }
    
    industry_domains = domain_templates.get(industry, domain_templates["service"])
    industry_businesses = business_components.get(industry, business_components["service"])
    
    for i in range(count):
        # Select a lead category
        category = random.choice(lead_categories)
        
        # Generate name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Create business name component
        business = random.choice(industry_businesses)
        if random.random() > 0.5:
            business += random.choice(industry_businesses).lower()
        
        # Generate email
        email_template = random.choice(industry_domains)
        email = email_template.format(
            name=first_name.lower(),
            initial=first_name[0].lower(),
            last=last_name.lower(),
            biz=business.lower()
        )
        
        # Create description based on category
        descriptions = {
            "Fashion Designers": [
                f"Independent fashion designer with a focus on sustainable clothing",
                f"Designer and founder of a boutique fashion label specializing in custom pieces",
                f"Fashion designer with expertise in {random.choice(['evening wear', 'casual wear', 'bridal', 'formal wear'])}"
            ],
            "Tailors": [
                f"Master tailor with over {random.randint(5, 20)} years of experience in bespoke clothing",
                f"Owner of a custom tailoring business specializing in {random.choice(['suits', 'formal wear', 'alterations', 'wedding attire'])}",
                f"Tailor with expertise in {random.choice(['mens suits', 'womens formal wear', 'traditional garments', 'denim'])}"
            ],
            "Software Developers": [
                f"Senior software developer specializing in {random.choice(['mobile apps', 'web development', 'cloud solutions', 'AI applications'])}",
                f"Lead developer at a tech startup focusing on {random.choice(['fintech', 'healthtech', 'edtech', 'e-commerce'])} solutions",
                f"Full-stack developer with expertise in {random.choice(['React', 'Node.js', 'Python', 'Java'])}"
            ]
        }
        
        # Get description based on category or generate a generic one
        if category in descriptions:
            description = random.choice(descriptions[category])
        else:
            description = f"{category} with expertise in {industry} solutions"
        
        # Generate relevance based on industry value props
        relevance = random.choice(industry_data["value_props"])
        
        leads.append({
            "name": full_name,
            "email": email,
            "description": description,
            "relevance": relevance
        })
    
    return leads

def enhance_lead_generation(business_data: Dict[str, Any], analysis: Dict[str, Any], count: int = 3) -> List[Dict[str, str]]:
    """
    Enhanced lead generation using industry-specific knowledge
    
    Args:
        business_data: Dictionary containing business information
        analysis: Dictionary containing business analysis results
        count: Number of leads to generate
        
    Returns:
        List of lead profiles
    """
    # Identify industry
    industry, confidence = identify_industry(business_data)
    
    # Generate leads based on the identified industry
    leads = get_industry_leads(industry, count)
    
    # If we have high confidence in our industry match, return these leads
    if confidence > 6.0:
        return leads
    
    # Otherwise, generate some leads using the analysis data too
    if analysis and isinstance(analysis, dict) and 'lead_type' in analysis:
        lead_types = analysis.get('lead_type', [])
        if not isinstance(lead_types, list):
            lead_types = [lead_types]
            
        # Add some generic leads based on the analysis
        for lead_type in lead_types[:2]:  # Just use the first two lead types
            # Create a generic lead for this type
            full_name = f"{random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
            
            leads.append({
                "name": full_name,
                "email": f"{full_name.lower().replace(' ', '.')}@example.com",
                "description": f"Professional in the {lead_type} industry",
                "relevance": f"Looking to partner with businesses like yours in the {industry} sector"
            })
    
    # Return the first 'count' leads
    return leads[:count] 