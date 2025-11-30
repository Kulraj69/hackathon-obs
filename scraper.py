import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    """
    Fetches and extracts text content from a URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Metadata
        title = soup.title.string if soup.title else ""
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title["content"]
            
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc["content"]
        og_desc = soup.find("meta", property="og:description")
        if og_desc and not description:
            description = og_desc["content"]

        # Remove script, style, nav, footer, header to get main content
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return {
            "title": title.strip(),
            "description": description.strip(),
            "text": cleaned_text[:10000]
        }
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
