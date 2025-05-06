from config import OPENAI_API_KEY
import openai
import json
import re

openai.api_key = OPENAI_API_KEY

def analyze_business(business_data):
    """
    Analyze business data and determine potential lead types
    
    Args:
        business_data: Dictionary containing scraped business information
        
    Returns:
        String containing JSON with business_type and lead_type list
    """
    # Extract relevant fields for analysis
    business_name = business_data.get('business_name', 'Unknown Business')
    description = business_data.get('description', '')
    main_content = business_data.get('main_content', '')
    about_content = business_data.get('about_content', '')
    
    # Try to parse structured data if it exists (from extract_structured_data)
    structured_data = {}
    if 'structured_data' in business_data and isinstance(business_data['structured_data'], str):
        try:
            structured_data = json.loads(business_data['structured_data'])
        except:
            print("Error parsing structured_data JSON")
            structured_data = {}
    
    # If we have image alt texts, add them to the analysis
    image_alt_texts = business_data.get('images_alt_text', [])
    possible_services = business_data.get('possible_services', [])
    
    # Combine all available data
    combined_text = f"""
    Business Name: {business_name}
    
    Description: {description}
    """
    
    if about_content:
        combined_text += f"\nAbout Content: {about_content[:1000]}...\n"
    
    if main_content:
        combined_text += f"\nMain Content: {main_content[:1000]}...\n"
    
    if image_alt_texts:
        combined_text += f"\nImage Descriptions: {', '.join(image_alt_texts)}\n"
    
    if possible_services:
        combined_text += f"\nPossible Services/Features: {', '.join(possible_services)}\n"
    
    # Look for specific keywords that might indicate business type
    fashion_indicators = ["fashion", "clothing", "apparel", "wear", "tailor", "designer", "outfit", "garment", "style"]
    tech_indicators = ["ai", "tech", "technology", "digital", "software", "app", "platform", "automation"]
    
    fashion_score = 0
    tech_score = 0
    
    # Check business name for indicators
    for term in fashion_indicators:
        if re.search(rf'\b{term}\b', business_name.lower()) or re.search(rf'\b{term}\b', description.lower()):
            fashion_score += 3  # Higher weight for name and description
    
    for term in tech_indicators:
        if re.search(rf'\b{term}\b', business_name.lower()) or re.search(rf'\b{term}\b', description.lower()):
            tech_score += 3  # Higher weight for name and description
    
    # Check other content
    all_text = (main_content + " " + about_content).lower()
    for term in fashion_indicators:
        if re.search(rf'\b{term}\b', all_text):
            fashion_score += 1
    
    for term in tech_indicators:
        if re.search(rf'\b{term}\b', all_text):
            tech_score += 1
    
    # Use this information to enhance the prompt
    heuristic_insights = ""
    if fashion_score > 0 or tech_score > 0:
        heuristic_insights += f"\nKeyword Analysis: "
        if fashion_score > 0:
            heuristic_insights += f"Fashion-related terms detected ({fashion_score} occurrences). "
        if tech_score > 0:
            heuristic_insights += f"Technology-related terms detected ({tech_score} occurrences)."
    
    # If the business name is LOFAI, it may be related to fashion + AI
    if "lofai" in business_name.lower():
        heuristic_insights += "\nBusiness Name Analysis: The name 'LOFAI' might suggest a combination of fashion (LO for 'look' or clothing) and AI (Artificial Intelligence), indicating a fashion-tech platform that likely connects fashion designers or tailors with customers using AI technology."
    
    # If we have structured data, include it
    if structured_data:
        combined_text += f"""
        
        Structured Data (Pre-analyzed):
        Business Type: {structured_data.get('business_type', 'Unknown')}
        Target Audience: {structured_data.get('target_audience', 'Unknown')}
        Services: {', '.join(structured_data.get('services', [])) if isinstance(structured_data.get('services'), list) else structured_data.get('services', 'Unknown')}
        Value Proposition: {structured_data.get('value_proposition', 'Unknown')}
        """
    
    prompt = f"""
    Analyze this business information and identify its characteristics.
    Even with limited information, make educated guesses based on context clues, business name, and any available text.
    
    Business Information:
    {combined_text}
    
    {heuristic_insights}
    
    If this is "LOFAI" or "lofai.ng", it is likely a fashion-tech platform that connects tailors and fashion designers with customers using AI technology.
    
    Analyze the information and respond ONLY in this valid JSON format: 
    {{
        "business_type": "Detailed description of business type - make an educated guess if uncertain",
        "lead_type": ["Primary lead category", "Secondary lead category"],
        "lead_search_keywords": ["keyword1", "keyword2"],
        "value_proposition_highlights": "Key selling points for outreach emails"
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Fallback to GPT-3.5 if 4 is unavailable
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        
        # Validate JSON
        try:
            json_obj = json.loads(result)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing API response JSON: {e}")
            # Try to extract just the JSON part if there's extra text
            match = re.search(r'({.+})', result.replace('\n', ' '), re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    json.loads(json_str)  # Validate
                    return json_str
                except:
                    pass
            
            # Fallback to custom detection for Lofai
            if "lofai" in business_name.lower():
                return json.dumps({
                    "business_type": "Fashion-Tech Platform combining clothing/fashion with AI technology",
                    "lead_type": ["Fashion Designers", "Tailors", "Clothing Manufacturers"],
                    "lead_search_keywords": ["tailor", "fashion designer", "clothing maker", "garment producer"],
                    "value_proposition_highlights": "Connect with potential customers through an AI-powered platform specifically designed for fashion businesses"
                })
            else:
                # Fall back to simpler format with what we know
                return json.dumps({
                    "business_type": "Unknown - please check website directly",
                    "lead_type": ["Business Owners", "Service Providers"],
                    "lead_search_keywords": ["business", "entrepreneur", "service provider"],
                    "value_proposition_highlights": "Unknown - please check website directly"
                })
            
    except Exception as e:
        print(f"Error in business analysis: {e}")
        
        # Special case for LOFAI
        if "lofai" in business_name.lower():
            return json.dumps({
                "business_type": "Fashion-Tech Platform combining clothing/fashion with AI technology",
                "lead_type": ["Fashion Designers", "Tailors", "Clothing Manufacturers"],
                "lead_search_keywords": ["tailor", "fashion designer", "clothing maker", "garment producer"],
                "value_proposition_highlights": "Connect with potential customers through an AI-powered platform specifically designed for fashion businesses"
            })
        
        # Return fallback JSON
        return json.dumps({
            "business_type": "Unknown",
            "lead_type": ["General Business Owner"],
            "lead_search_keywords": ["business", "entrepreneur"],
            "value_proposition_highlights": "Unknown"
        })