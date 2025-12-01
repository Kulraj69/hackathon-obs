import os
import serpapi
from dotenv import load_dotenv

load_dotenv()

def search_hackathons(query="hackathons", num_results=10):
    """
    Searches for hackathons using SerpApi (new library).
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY not found in environment variables")

    client = serpapi.Client(api_key=api_key)
    results = client.search({
        "engine": "google",
        "q": query,
        "num": num_results
    })
    
    links = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            links.append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet")
            })
    
    return links

if __name__ == "__main__":
    # Test the search
    print(search_hackathons("upcoming hackathons devpost"))
