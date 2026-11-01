### Week 2 UDEMY Project Review

## LLM ChatBot ToneShift LAB

This project is based of a lab on an already live consumer application called **ToneShift** 

Link to ToneShift: *https://newroads.scot/toneshift*

# Understanding the project files

1. *sales_brochure_generator*
2. *multi-turn_conversation*
3. *scraper*
4. *chatbot*

# Overview

- Sales Brochure Generator: Script to generate sales brochure by scraper companies URL of choosing. 
- Multi Turn Conversation: Setting up two different LLM's to converse with each other.
- Scraper: Supporting files, given by the course Admin used for scraping links, and contents of a chosen website.
- ToneShift Lab ChatBot (Main project aspiration for week 2): Small scale ToneShift copy, with a front-end using gradio, supporting 4 tones. 
- *Note: This project has only been configured and setup for OpenAI users. If you are planning on using another LLM it would be recommended to still use the OpenAI SDK and input a base_url so long as the LLM of your choice supports this funcitonality.*

## ToneShift Lab ChatBot

**What is ToneShift?**

*ToneShift* is a re-writing tool, that takes a given **Message** and a given **Tone** from the user, and re-writes it in the **Tone** specified.

*ToneShift* supports 4 tones:   
    - Professional  
    - Flirty  
    - Assertive  
    - Angry

## How To Run

1. After checking out the branch ensure that you create a .env file containg your OpenAI API key (in the var `OPENAI_API_KEY`) or respective LLM of choice.
2. cd into udemy-projects, then week_02/src
3. Then initialize & activate a virtual environment (`uv sync` if using uv)
4. Ensure you sync and install all dependencies in the .toml file cloned within this repo. (`uv sync` does this for you already)
5. Open a new instance of your terminal and type `python chatbot.py`
6. Click the localhost link produced in the terminal, and you can then test ToneShift. (Ctrl + C to shut down the Gradio server)

*Note: Never commit .env*

## Tools Created

- strip_pii: Tool to scrub users message if any emails are found, runs whenever an email is detected in a message
- critique_tone: Small validation tool to ensure the message being output from the LLM meets a character count.

## What I've Learned

- Agentic LLM design patterns, tool creation and, control flow tooling usage.
- Regex for Personal Identification Information, function_call loop, gradio failure returns






