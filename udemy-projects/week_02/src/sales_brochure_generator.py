from openai import OpenAI 
import gradio as gr 
from dotenv import load_dotenv 
from scraper import fetch_website_contents
import os 


load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

gemini_client = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
openai_client = OpenAI(api_key=openai_key)

system_prompt = """ You are to make a fun and high converting sales brochure using the contents of the website that is given to you.
                    Make sure you return this in Markdown  """ 

# Create a streamed brochure using gradio's interface 

# LLM call for each model 
def gpt_call(prompt): 
    messages = [{"role" : "system", "content" : system_prompt}, {"role" : "user", "content" : prompt}]
    stream = openai_client.chat.completions.create(model='gpt-4.1-mini', messages=messages, stream=True) 
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result

def gemini_call(prompt): 
    messages = [{"role" : "system", "content" : system_prompt}, {"role" : "user", "content" : prompt}]
    stream = gemini_client.chat.completions.create(model='gemini-2.5-flash', messages=messages, stream=True) 
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result

# Streaming function to either LLM 
def stream_models(company_name, url, model): 
    yield ""
    prompt = f"Please generate a company brochure for {company_name}. Here is their landing page:\n"
    prompt += fetch_website_contents(url)
    if model == 'GPT': 
        result = gpt_call(prompt)
    elif model == 'Gemini':
        result = gemini_call(prompt)
    else: 
        raise ValueError('Unkown Model')
    yield from result

# Create the Gradio interface

gradio_input = gr.Textbox(label='Enter your company name here:', lines=1)
gradio_input_url = gr.Textbox(label='Input your website URL here:')
gradio_output = gr.Markdown(label='Response:')
gradio_dropdown = gr.Dropdown(choices=['GPT', 'Gemini'])

gradio = gr.Interface(fn=stream_models,
                      title='Sales Brochure Generator', 
                      inputs=[gradio_input, gradio_input_url,gradio_dropdown], 
                      outputs=[gradio_output], 
                      flagging_mode='never',
                      examples=[["Hugging Face", "https://huggingface.co", "GPT"],
                                ["Edward Donner", "https://edwarddonner.com", "Gemini"]
                            ])
    
gradio.launch()

