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
        
        scraped_data = scrape_url(url)
        if not scraped_data:
            continue
            
        text_content = scraped_data['text']
        
        print("  Extracting details...")
        details = extract_hackathon_details(text_content)
        
        if details:
            # Check if it's actually a hackathon
            if not details.get('is_hackathon', True): # Default to True if key missing to be safe, but prompt should return it
                print(f"  Skipping: Not a specific hackathon event ({details.get('name')})")
                continue

            details['url'] = url
            # Use scraped title if available and better than search title
            if scraped_data.get('title'):
                details['name'] = scraped_data['title']
            elif not details.get('name'):
                details['name'] = item['title']
                
            # Use scraped description if LLM/Regex failed to get a good one
            if not details.get('description') or len(details.get('description', '')) < 10:
                details['description'] = scraped_data.get('description', '')[:200]
            
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
