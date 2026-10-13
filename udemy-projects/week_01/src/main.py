from multiprocessing import parent_process
from openai import OpenAI 
from dotenv import load_dotenv
from scraper import fetch_website_contents
from link_parser import relevant_links
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

url = "https://www.newroads.scot"

brochure_system_prompt = """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a short brochure about the company for prospective customers, investors and recruits.
    Respond in markdown without code blocks.
    Include details of company culture, customers and careers/jobs if you have the information.
"""

# Fetch content from main page and relevant links append into one result 
# Generate sales brochure from the contents 

def get_all_content(url : str) -> str: 
    main_content = fetch_website_contents(url)
    links = relevant_links(url)
    result = f"##Main Page Content: {main_content}"
    for link in links["links"]: 
        result += f"\n\n ##Link Content {link['type']}: {fetch_website_contents(link['url'])}"
    
    return result

def brochure_user_prompt(company_name: str, url: str) -> str: 
    user_prompt = f"""
        You are looking at a company called: {company_name}
        Here are the contents of its landing page and other relevant pages;
        use this information to build a short brochure of the company in markdown without code blocks.\n\n
    """
    user_prompt += get_all_content(url)
    user_prompt = user_prompt[:5_000]
    return user_prompt 

def generate_brochure(company_name: str, url: str) -> str: 
    messages = [{"role" : "system", "content" : brochure_system_prompt}, {"role" : "user", "content" : brochure_user_prompt(company_name, url)}]
    stream = client.responses.create(model="gpt-6.1-sol", input=messages, stream=True)
    response = ""
    for chunk in stream:
        if chunk.type == "response.output_text.delta":
            response += chunk.delta
            print(chunk.delta, end="", flush=True)

    print()
    return response

generate_brochure("New Roads International", url)