import os
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

BASE_URL = "https://api.freshservice.com"
TARGET_SECTIONS = [
    "#tickets",                      
    "#view_a_ticket",                
    "#filter_tickets",               
    "#create_ticket",                
    "#authentication",               
    "#view_all_ticket",              
    "#update_a_ticket",              
    "#move_a_ticket",                
    "#delete_a_ticket",              
    "#delete_a_ticket_attachment",  
    "#restore_a_ticket",             
    "#schema",                       
    "#post-tickets",                 
    "#ticket_attributes",            
    "#view_all_ticket_fields",       
    "#create_ticket_with_attachment",
    "#create_service_request"        
]


os.makedirs("output", exist_ok=True)

def scrape_freshservice_docs(base_url, sections):
    """Scrape multiple sections of Freshservice API docs"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")   
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )

    all_data = []
    
    for section in sections:
        try:
            url = f"{base_url}/{section}"
            print(f"🔍 Scraping: {url}")
            
            driver.get(url)
            time.sleep(5)  # Wait for content to load
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            section_data = extract_section_content(soup, section)
            
            if section_data:
                all_data.extend(section_data)
                print(f"✅ Found {len(section_data)} content blocks in {section}")
            else:
                print("No content found")
                
        except Exception as e:
            print(f"Error scraping {section}: {e}")
            continue
    
    driver.quit()
    return all_data

def extract_section_content(soup, section_name):
    """Extract content from a section with better structure"""
    data = []
    
    # Look for the main content area
    content_areas = [
        soup.find("div", {"class": "content"}),
        soup.find("main"),
        soup.find("article"),
        soup.find("div", {"id": "main"}),
        soup.find("body")
    ]
    
    main_content = None
    for area in content_areas:
        if area:
            main_content = area
            break
    
    if not main_content:
        return data
    
    headers = main_content.find_all(["h1", "h2", "h3", "h4"])
    
    for header in headers:
        title = header.get_text(strip=True)
        if not title:
            continue
            
        content = []
        current = header.find_next_sibling()
        
        while current and current.name not in ["h1", "h2", "h3", "h4"]:
            content_text = extract_element_content(current)
            if content_text:
                content.extend(content_text)
            current = current.find_next_sibling()
        
        if content:
            data.append({
                "section": f"{section_name.replace('#', '')} - {title}",
                "content": content
            })
    
    code_blocks = main_content.find_all(["pre", "code"])
    for i, code in enumerate(code_blocks):
        code_text = code.get_text(strip=True)
        if code_text and len(code_text) > 20:  # Only substantial code
            data.append({
                "section": f"{section_name.replace('#', '')} - Code Example {i+1}",
                "content": [code_text]
            })
    
    return data

def extract_element_content(element):
    """Extract meaningful content from an element"""
    if not element:
        return []
    
    content = []
    
    if element.name == "p":
        text = element.get_text(" ", strip=True)
        if text:
            content.append(text)
            
    elif element.name in ["pre", "code"]:
        code_text = element.get_text(strip=True)
        if code_text:
            content.append(f"```\n{code_text}\n```")
            
    elif element.name == "ul":
        items = []
        for li in element.find_all("li"):
            item_text = li.get_text(" ", strip=True)
            if item_text:
                items.append(f"• {item_text}")
        if items:
            content.append("\n".join(items))
            
    elif element.name == "ol":
        items = []
        for i, li in enumerate(element.find_all("li"), 1):
            item_text = li.get_text(" ", strip=True)
            if item_text:
                items.append(f"{i}. {item_text}")
        if items:
            content.append("\n".join(items))
            
    elif element.name == "table":
        rows = []
        for row in element.find_all("tr"):
            cols = [col.get_text(" ", strip=True) for col in row.find_all(["th", "td"])]
            if cols and any(cols):  
                rows.append(cols)
        if rows:
            content.append({"table": rows})
            
    elif element.name == "blockquote":
        quote_text = element.get_text(" ", strip=True)
        if quote_text:
            content.append(f"> {quote_text}")
            
    elif element.name == "div":
        text = element.get_text(" ", strip=True)
        if text and len(text) > 10:  
            content.append(text)
    
    return content

def save_raw_html_for_debugging(soup, filename):
    """Save raw HTML for debugging purposes"""
    with open(f"output/debug_{filename}.html", "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

if __name__ == "__main__":
    print("Enhanced Freshservice API documentation scraping...")
    
    test_url = f"{BASE_URL}/#ticket_attributes"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🔍 Testing main page structure: {test_url}")
        driver.get(test_url)
        time.sleep(7)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        save_raw_html_for_debugging(soup, "main_page")
        
        nav_links = []
        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if href.startswith("#") and text:
                nav_links.append((href, text))
        
        print(f"Found {len(nav_links)} navigation links")
        for href, text in nav_links[:10]:  # first 10
            print(f"  - {text}: {href}")
        
        if nav_links:
            found_sections = [href for href, text in nav_links if "ticket" in text.lower() or "create" in text.lower() or "auth" in text.lower()]
            if found_sections:
                print(f"Using discovered sections: {found_sections}")
                TARGET_SECTIONS.extend(found_sections[:5])  
    
    except Exception as e:
        print("⚠️ Error in initial analysis:")
    
    finally:
        driver.quit()
    
    # Now scrape all sections
    docs_data = scrape_freshservice_docs(BASE_URL, TARGET_SECTIONS)
    
    if docs_data:
        output_file = os.path.join("output", "freshservice_docs.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)
        
        print(f"Enhanced scraping completed!")
        print(f"Collected {len(docs_data)} sections")
        print(f"Data saved to {output_file}")
        
        # Show summary
        section_counts = {}
        for item in docs_data:
            section = item["section"].split(" - ")[0]
            section_counts[section] = section_counts.get(section, 0) + 1
        
        print("\nSection Summary:")
        for section, count in section_counts.items():
            print(f"  - {section}: {count} items")
    else:
        print("No data was scraped. Check the URL and selectors.")