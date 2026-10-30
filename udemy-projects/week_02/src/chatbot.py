from dotenv import load_dotenv
from enum import Enum
import os
import re
import json
from openai import OpenAI

class Tones(Enum): 
    FLIRTY = 1
    ASSERTIVE = 2
    ANGRY = 3
    PROFESSIONAL = 4

system_prompts  = { 
    Tones.FLIRTY: """ You are going to recieve a message, ensure you sanitize first if needed then rewrite.
                    You have to ensure that it gets re-written in a flirty tone. 
                    Make sure the message is seductive, playful, and forward. 
                    Don't be shy to make plans or ask to see the person if the message offers that. 
                    Act as if they already want you, have lots of confidence.
                    Keep it short sometimes flirting is all about what is not said more than what is said. 
                """, 

    Tones.ASSERTIVE: """ You are going to recieve a message, ensure you sanitize first if needed then rewrite.
                    You have to ensure that it gets re-written in a assertive tone. 
                    Make sure the message is forward, direct, and unforgiving. 
                    Don't be shy to tell it how things are, you mean what you say always. 
                    Act as if you operate with nothing to lose at all.
                    Assesrtion is all about having you put your foot down and not want to look the other way. 
                """,

                
    Tones.ANGRY: """ You are going to recieve a message, ensure you sanitize first if needed then rewrite.
                    You have to ensure that it gets re-written in a angry tone. 
                    Make sure the message is abrasive, concise, and rage-induced. 
                    Don't be shy to sprinkle any bad words or vocab you would think is taboo in there. 
                    Act as if they have really wronged you in a really shitty way.
                    The length of the message shouldn't be longer than 5 lines, eventhough you have a lot to say shorten it if you can. 
                """,
                
    Tones.PROFESSIONAL: """ You are going to recieve a message, ensure you sanitize first if needed then rewrite.
                    You have to ensure that it gets re-written in a professional tone. 
                    Make sure the message is coridal, polite, and accurate. 
                    Use sophisticated vocabulary that is fit for an office setting.
                    Treat them with the respect as if they were your boss, eventhough they aren't sometimes. 
                    The length of the message shouldn't be longer than 5 lines.
                """ 
}

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

'''
1. One dumb happy path
Script or notebook: hard-coded message + tone → model returns a rewrite. Prove the API works before any UI/tools.

2. Clean function: rewrite(message, tone) -> str
Move that into a small Python module. Add 2-3 tones as an enum/list. Print results for a few examples.

3. First real tool (function-calling)
One tool only, e.g. estimate_length or strip_pii (emails/phones). Wire the model so it must call the tool when useful — verify in logs that the tool ran.

4. Second tool
e.g. critique_tone(original, rewrite, tone) -> feedback or a hard reject if rewrite is empty/too long. Keep tools boring and testable.

5. Thin UI
Gradio (or similar): text box + tone dropdown + submit → show rewrite (+ optional “tools used” panel). No fancy design.

6. Glue + failure modes
Empty input, API errors, tool failures — show a clear message instead of crashing.

7. README + push
What it is, how to run, which tools exist, what you learned from Week 2, link to live ToneShift product. Commit early and often.

'''

tools = [
    {
        "type": "function",
        "name": "strip_pii",
        "description": "Call this when the user message contains any email addresses before rewriting, use the returned sanitized text as the content to rewrite; don't echo raw emails.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "the message that the user has input containing sensitive information like an email.",
                },
            },
            "required": ["message"],
        },
    },
]

def strip_pii(message: str) -> str:

     if "@" in message:
        pattern = r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b"
        final_string = re.sub(pattern, "[EMAIL]", message)
     else: 
        return message

     return final_string

def rewrite(message: str, tone: str) -> str:

    system_prompt = None

    for selected_tone in Tones:
        if tone.lower() == selected_tone.name.lower():
            system_prompt = system_prompts[selected_tone]
            break
    if system_prompt is None: 
        raise ValueError('Tone not supported')

    running_history = [{"role":"system", "content": system_prompt}, 
               {"role": "user", "content" : message}]

    response = client.responses.create(model='gpt-5.1', input=running_history, tools=tools, tool_choice="auto")
    print(f"Here's the response output for the first API call: {response.output}")

    running_history += response.output
    print(f"Here's the running history containing the first API call: {running_history}")

    for item in response.output:
        if item.type == 'function_call': 
            if item.name == 'strip_pii':
                message = json.loads(item.arguments)['message']
                sanitized_message = strip_pii(message)
                print(item.call_id)
                running_history.append(
                    {
                        "type": "function_call_output", 
                        "call_id": item.call_id,
                        "output": sanitized_message 
                    }
                )
                print(f"Here's the santized message ready for the next call: {sanitized_message}")
                response = client.responses.create(model='gpt-5.1', input=running_history, tools=tools)
        else: 
            print("There was no need to sanitize the message.")
            break
   

    return response.output_text

print(rewrite('I think I can get those reports by monday but Im not really how fast I can get the data from marketing, Ive emailed akhil@gmail.com, and Im waiting for his response.', 'professional'))