import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import json

load_dotenv()

def extract_hackathon_details(text):
    """
    Uses Llama via Hugging Face to extract hackathon details.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        print("HF_TOKEN not found. Skipping extraction.")
        return None

    client = InferenceClient(api_key=token)
    
    prompt = f"""
    You are a helpful assistant that extracts structured data from text.
    Analyze the following text describing a hackathon and extract the following details in JSON format:
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
    {text[:4000]}
    
    JSON Output:
    """
    
    try:
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct", # Using a solid default, can be changed
            messages=messages,
            max_tokens=500,
            stream=False
        )
        
        content = response.choices[0].message.content
        
        # specific cleanup for json
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            print("Could not find JSON in response")
            return None

    except Exception as e:
        print(f"Error calling HF API: {e}")
        return None
