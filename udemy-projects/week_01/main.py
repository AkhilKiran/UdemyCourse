import os
from openai import OpenAI
from dotenv import load_dotenv
from scraper import fetch_website_contents

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

toneshift_url = "https://www.newroads.scot/toneshift"
toneshift_contents = fetch_website_contents(toneshift_url)

message = "Summarize the contents of the website in a short, snarky, humorous way. The website contents are:"

system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

def summarize_website(url): 
    contents = fetch_website_contents(url)
    messages = [{"role": "user", "content": message + contents },
                {"role": "system", "content": system_prompt}]
    response = client.responses.create(model="gpt-4.1-nano", input = messages) 
    return response.output_text

print(summarize_website(toneshift_url))