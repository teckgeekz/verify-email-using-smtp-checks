# utils/linkedin_scraper.py
import os
import requests

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def find_linkedin_profile(name, company):
    query = f'site:linkedin.com/in "{name}" "{company}"'
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if "organic" in data:
        for result in data["organic"]:
            if "linkedin.com/in" in result["link"]:
                return result["link"], result.get("title")
    return None, None
