import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_hackathon_details(text):
    """
    Uses Llama 3.1 via Hugging Face (OpenAI compatible API) to extract hackathon details.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        print("HF_TOKEN not found. Skipping extraction.")
        return None

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=token,
    )
    
    prompt = f"""
    You are a helpful assistant that extracts structured data from text.
    Analyze the following text and determine if it describes a SPECIFIC upcoming or ongoing hackathon event.
    
    Ignore:
    - Blog posts about hackathons in general
    - Lists of hackathon platforms
    - Tutorials on how to win hackathons
    - Past events (unless they are recurring and have a new date)
    
    If it is NOT a specific hackathon event, return JSON with "is_hackathon": false.
    
    If it IS a specific hackathon, extract the following details in JSON format:
    - is_hackathon: true
    - name: Name of the hackathon
    - deadline: Submission deadline (YYYY-MM-DD format if possible, or text)
    - start_date: Start date
    - end_date: End date
    - tech_stack: List of technologies required or recommended
    - company: Organizing company or sponsor
    - description: Brief description (max 1 sentence)
    - prize: Prize pool or main prize
    
    If a field is not found, use null.
    
    Text:
    {text[:10000]}
    
    JSON Output:
    """
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct", 
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"Error calling HF API: {e}")
        return None
