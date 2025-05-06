from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright
from time import sleep
import re
import openai
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Static scraping (BeautifulSoup)
def scrape_static(url, max_retries=3):
    for _ in range(max_retries):
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                timeout=10
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            business_name = soup.title.string if soup.title else "N/A"
            description = soup.find("meta", attrs={"name": "description"})
            description = description["content"] if description else "N/A"
            
            # Extract main content text
            main_content = ""
            
            # Common content containers
            content_elements = soup.select("main, article, .content, #content, .main, #main")
            if not content_elements:
                # Fallback to body text if no specific content containers
                paragraphs = soup.find_all("p")
                main_content = " ".join([p.get_text().strip() for p in paragraphs[:10]]) # First 10 paragraphs
            else:
                for element in content_elements[:1]:  # Use first main content element
                    paragraphs = element.find_all("p")
                    main_content = " ".join([p.get_text().strip() for p in paragraphs])
            
            # Try to extract about page URL
            about_links = []
            for a in soup.find_all("a", href=True):
                if re.search(r'about|company|team|who we are', a.get_text().lower()):
                    about_url = a['href']
                    # Handle relative URLs
                    if not about_url.startswith('http'):
                        if about_url.startswith('/'):
                            base_url = '/'.join(url.split('/')[:3])  # http(s)://domain.com
                            about_url = base_url + about_url
                        else:
                            about_url = url.rstrip('/') + '/' + about_url
                    about_links.append(about_url)
            
            result = {
                "business_name": business_name,
                "description": description,
                "main_content": main_content,
                "about_links": about_links[:1] if about_links else []  # Only use first about link
            }
            
            # If we have an about page, try to scrape it too
            if about_links:
                try:
                    about_response = requests.get(
                        about_links[0],
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                        timeout=10
                    )
                    about_soup = BeautifulSoup(about_response.text, 'html.parser')
                    about_paragraphs = about_soup.find_all("p")
                    about_content = " ".join([p.get_text().strip() for p in about_paragraphs[:10]])
                    result["about_content"] = about_content
                except Exception as e:
                    print(f"Error scraping about page: {e}")
            
            return result
            
        except Exception as e:
            print(f"Retry {_ + 1}: Error scraping {url} - {str(e)}")
            sleep(2)
    
    # Static scraping failed, but return None to allow fallback to dynamic
    print("Static scraping failed after all retries")
    return None

# Dynamic scraping (Playwright)
def scrape_dynamic(url):
    try:
        with sync_playwright() as p:
            # Use Chromium with specific options for better compatibility
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-web-security', '--disable-features=IsolateOrigins', '--disable-site-isolation-trials']
            )
            
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            page = context.new_page()
            page.goto(url, timeout=30000)  # 30-second timeout
            
            # Wait longer for page to fully load
            page.wait_for_selector("body")
            sleep(3)  # Give extra time for JS to execute
            
            # Get page source
            page_source = page.content()
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract basic info
            business_name = page.title()
            
            # Get meta description
            description = page.query_selector("meta[name='description']")
            description = description.get_attribute("content") if description else "N/A"
            
            # Extract all text from main elements (more comprehensive)
            main_elements = page.query_selector_all("main, article, .content, #content, .main, #main")
            main_content = ""
            
            if main_elements:
                for element in main_elements:
                    content = page.evaluate("el => el.textContent", element)
                    if content:
                        main_content += content.strip() + " "
            else:
                # Get all visible text from paragraphs, headings, divs with substantial text
                text_elements = page.query_selector_all("p, h1, h2, h3, h4, h5, h6, li, span, div")
                for element in text_elements:
                    try:
                        is_visible = page.evaluate("""element => {
                            const style = window.getComputedStyle(element);
                            return style.display !== 'none' && 
                                  style.visibility !== 'hidden' && 
                                  style.opacity !== '0' &&
                                  element.offsetWidth > 0 &&
                                  element.offsetHeight > 0;
                        }""", element)
                        
                        if is_visible:
                            content = page.evaluate("el => el.textContent", element)
                            # Only include elements with substantial text (at least 20 chars)
                            if content and len(content.strip()) > 20:
                                main_content += content.strip() + " "
                    except Exception as e:
                        continue
            
            # Look for about page links
            about_links = []
            links = page.query_selector_all("a")
            for link in links:
                try:
                    text = page.evaluate("el => el.textContent", link)
                    href = page.evaluate("el => el.href", link)
                    if text and href and re.search(r'about|company|team|who we are', text.lower()):
                        about_links.append(href)
                except:
                    continue
            
            # Extract all images with alt text - these can provide valuable context
            images = []
            img_elements = page.query_selector_all("img[alt]:not([alt=''])")
            for img in img_elements:
                try:
                    alt = page.evaluate("el => el.alt", img)
                    if alt and len(alt) > 3:  # Only meaningful alt text
                        images.append(alt)
                except:
                    continue
            
            # Get service/offering sections - often in list items or cards
            services = []
            service_elements = page.query_selector_all(".service, .product, .offering, .feature, .card, li")
            for element in service_elements:
                try:
                    content = page.evaluate("el => el.textContent", element)
                    if content and len(content.strip()) > 15 and len(content.strip()) < 200:
                        services.append(content.strip())
                except:
                    continue
            
            result = {
                "business_name": business_name,
                "description": description,
                "main_content": main_content[:5000],  # Limit to avoid overly large content
                "about_links": about_links[:1] if about_links else [],
                "images_alt_text": images[:10],  # First 10 images with alt text
                "possible_services": services[:10]  # First 10 possible services
            }
            
            # Visit about page if found
            if about_links:
                try:
                    about_page = context.new_page()
                    about_page.goto(about_links[0], timeout=15000)
                    about_page.wait_for_selector("body")
                    sleep(2)  # Give time for JS to execute
                    
                    about_content = ""
                    about_text_elements = about_page.query_selector_all("p, h1, h2, h3, h4, h5, h6, li")
                    for element in about_text_elements:
                        try:
                            is_visible = about_page.evaluate("""element => {
                                const style = window.getComputedStyle(element);
                                return style.display !== 'none' && 
                                    style.visibility !== 'hidden' && 
                                    style.opacity !== '0';
                            }""", element)
                            
                            if is_visible:
                                content = about_page.evaluate("el => el.textContent", element)
                                if content and len(content.strip()) > 20:
                                    about_content += content.strip() + " "
                        except:
                            continue
                    
                    result["about_content"] = about_content[:5000]  # Limit size
                    about_page.close()
                except Exception as e:
                    print(f"Error scraping about page: {e}")
            
            # Take a screenshot for debugging or content analysis
            try:
                page.screenshot(path="output/screenshot.png")
                result["screenshot_path"] = "output/screenshot.png"
            except:
                pass
            
            browser.close()
            
            # Log the scraped contents for debugging
            with open("output/scrape_result.json", "w") as f:
                json.dump(result, f, indent=2)
                
            return result
            
    except Exception as e:
        print(f"Dynamic scraping failed: {e}")
        return None

def extract_structured_data(scrape_results):
    """Use LLM to extract structured data from scraped content"""
    if not scrape_results:
        return {}
    
    # Save raw scrape results to output directory for debugging
    try:
        with open("output/raw_scrape.json", "w") as f:
            json.dump(scrape_results, f, indent=2)
    except:
        pass
    
    # Combine all scraped text
    all_content = ""
    
    # Business name and description
    all_content += f"Business Name: {scrape_results.get('business_name', 'N/A')}\n\n"
    all_content += f"Meta Description: {scrape_results.get('description', 'N/A')}\n\n"
    
    # Add image alt texts if available
    if scrape_results.get('images_alt_text'):
        all_content += f"Image Descriptions: {', '.join(scrape_results.get('images_alt_text'))}\n\n"
    
    # Add possible services if available
    if scrape_results.get('possible_services'):
        all_content += f"Possible Services/Features: {', '.join(scrape_results.get('possible_services'))}\n\n"
    
    # Add about content if available
    if scrape_results.get('about_content'):
        all_content += f"About Content: {scrape_results.get('about_content', 'N/A')[:1500]}\n\n"
    
    # Add main content (limited to avoid token limits)
    if scrape_results.get('main_content'):
        all_content += f"Main Content: {scrape_results.get('main_content', 'N/A')[:1500]}\n\n"
    
    # Fallback to simpler analysis if we don't have enough data
    if len(all_content) < 100:
        return json.dumps({
            "business_name": scrape_results.get('business_name', 'N/A'),
            "business_type": "Could not determine - insufficient data",
            "target_audience": "Could not determine - insufficient data",
            "services": ["Could not determine - insufficient data"],
            "value_proposition": "Could not determine - insufficient data"
        })
    
    # Save the compiled content for debugging
    try:
        with open("output/compiled_content.txt", "w") as f:
            f.write(all_content)
    except:
        pass
        
    prompt = f"""
    Extract structured information from this website text. Even if information is limited, 
    make your best educated guess based on the available clues:
    
    {all_content}
    
    Extract and return ONLY a JSON object with these fields:
    1. business_name: The name of the business
    2. business_type: The type/category of business (e.g., e-commerce, SaaS, marketplace)
    3. target_audience: Who the business serves (e.g., "small businesses", "fashion designers")
    4. services: List of main products or services offered
    5. value_proposition: What makes this business unique
    
    If you can't determine something with certainty, make an educated guess based on context clues and clearly mark it with "GUESS: ".
    Return ONLY valid JSON with no explanation.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        
        # Try to parse JSON to verify it's valid
        try:
            parsed = json.loads(result)
            return result
        except json.JSONDecodeError as e:
            print(f"Invalid JSON returned from OpenAI: {e}")
            # Try to extract just the JSON part if there's extra text
            match = re.search(r'({.+})', result.replace('\n', ' '), re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    parsed = json.loads(json_str)
                    return json_str
                except:
                    pass
            
            # Fallback to manual structure
            return json.dumps({
                "business_name": scrape_results.get('business_name', 'N/A'),
                "business_type": "Error in parsing LLM response",
                "target_audience": "Error in parsing LLM response",
                "services": ["Error in parsing LLM response"],
                "value_proposition": "Error in parsing LLM response"
            })
            
    except Exception as e:
        print(f"Error extracting structured data: {e}")
        # Return manual structure with the data we have
        return json.dumps({
            "business_name": scrape_results.get('business_name', 'N/A'),
            "business_type": "GUESS: Based on name, possibly a fashion or AI platform",
            "target_audience": "GUESS: Fashion consumers or businesses",
            "services": ["GUESS: Fashion services", "GUESS: AI-assisted recommendations"],
            "value_proposition": "GUESS: Integration of fashion and AI technology"
        })