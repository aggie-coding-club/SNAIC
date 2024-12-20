from serpapi import GoogleSearch
import dotenv
import os

dotenv.load_dotenv()

import image_url_getter

params = {
  "engine": "google_lens",
  "url": image_url_getter.image_url, #using imgur api to get links from local image but can see if there's a way to use local images
  "api_key": os.getenv('SERP_KEY')
}

search = GoogleSearch(params)
results = search.get_dict()
links = results.get("visual_matches")
print(links)
#visual matches are in results.json
#next steps would be to find which one appears most and get amazon link for that