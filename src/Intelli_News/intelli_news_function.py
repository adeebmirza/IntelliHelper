import requests
from dotenv import load_dotenv
import os
load_dotenv()

BING_API_KEY = os.getenv("BING_API_KEY")

# Bing News Search API endpoints
BING_NEWS_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/news/search"
BING_NEWS_LATEST_URL = "https://api.bing.microsoft.com/v7.0/news"


def search_bing_news(query):
    headers = {'Ocp-Apim-Subscription-Key': BING_API_KEY}
    params = {'q': query, 'textDecorations': True, 'textFormat': "HTML", 'originalImg': True, 'count': 20}
    try:
        response = requests.get(BING_NEWS_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get('value', [])
        
        # Extract high-quality image URLs if available
        for result in results:
            if 'image' in result and 'contentUrl' in result['image']:
                result['image_url'] = result['image']['contentUrl']
            elif 'image' in result and 'thumbnail' in result['image']:
                result['image_url'] = result['image']['thumbnail']['contentUrl']
            else:
                result['image_url'] = None  # No image available

        return results
    except (requests.exceptions, ValueError) as e:
        print(f"Error fetching Bing News: {e}")
        return []

def get_latest_news():
    headers = {'Ocp-Apim-Subscription-Key': BING_API_KEY}
    params = {'textDecorations': True, 'textFormat': "HTML", 'originalImg': True, 'count': 20}
    try:
        response = requests.get(BING_NEWS_LATEST_URL, headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get('value', [])
        
        # Extract larger images if available
        for result in results:
            if 'image' in result and 'contentUrl' in result['image']:
                result['image_url'] = result['image']['contentUrl']
            elif 'image' in result and 'thumbnail' in result['image']:
                result['image_url'] = result['image']['thumbnail']['contentUrl']
            else:
                result['image_url'] = None  # No image available
        return results
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching latest Bing News: {e}")
        return []
