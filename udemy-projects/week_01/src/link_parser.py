from openai import OpenAI 
from dotenv import load_dotenv
import os
import json
from scraper import fetch_website_links

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# Step 1: Fetch links
# Step 2: Filter for relevant links through LLM, and return as formatted JSON using a system prompt
# Step 3: Convert to python dict for read access using json.loads()
def relevant_links(url : str) -> dict: 
    links = fetch_website_links(url)
    link_system_prompt = """
    You are provided with a list of links found on a webpage.
    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    such as links to an About page, or a Company page, or Careers/Jobs pages.
    You should respond in JSON as in this example: 

    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """
    user_prompt = f"""
        Here's the links that I've scraped from the landing page: {links}
        We are going to make a sales brochure out of these links and website, so ensure you get all the relevant ones for this task. 
        Respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.
    """

    messages = [{"role" : "system", "content" : link_system_prompt}, {"role" : "user", "content" : user_prompt}]
    response = client.responses.create(model='gpt-6.1-sol', input=messages)
    data = json.loads(response.output_text)
    print(f"Amount of relevant links found: {len(data['links'])}")
    return data
