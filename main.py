import time
from search import search_hackathons
from scraper import scrape_url
from llm import extract_hackathon_details
from sheets import update_sheet, setup_headers

def main():
    print("Starting Hackathon Scout Agent...")
    
    # 1. Search for hackathons
    queries = [
        "site:devpost.com upcoming hackathons",
        "site:devfolio.co hackathons",
        "site:unstop.com hackathons",
        "site:hackerearth.com challenges",
        "site:hack2skill.com hackathons"
    ]
    
    all_links = []
    seen_urls = set()
    
    for query in queries:
        print(f"Searching for: {query}")
        results = search_hackathons(query, num_results=5) # Keep it low for testing
        for res in results:
            url = res['link']
            if url not in seen_urls:
                all_links.append(res)
                seen_urls.add(url)
        time.sleep(2) # Be nice to the API
        
    print(f"Found {len(all_links)} unique links.")
    
    hackathons_data = []
    
    # 2. Scrape and Extract
    for item in all_links:
        url = item['link']
        print(f"Processing: {url}")
        
        text_content = scrape_url(url)
        if not text_content:
            continue
            
        print("  Extracting details...")
        details = extract_hackathon_details(text_content)
        
        if details:
            details['url'] = url
            # Fallback for name if LLM misses it
            if not details.get('name'):
                details['name'] = item['title']
            
            hackathons_data.append(details)
            print(f"  Found: {details.get('name')}")
        else:
            print("  Could not extract details.")
            
        time.sleep(1) # Rate limiting
        
    # 3. Update Sheet
    if hackathons_data:
        print(f"Updating Google Sheet with {len(hackathons_data)} entries...")
        setup_headers() # Ensure headers exist
        update_sheet(hackathons_data)
        print("Done!")
    else:
        print("No data found to update.")

if __name__ == "__main__":
    main()
