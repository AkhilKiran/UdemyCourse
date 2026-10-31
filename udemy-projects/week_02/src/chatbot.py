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
    Tones.FLIRTY: """ You are going to recieve a message, ensure you sanitize first when message contains any email, then rewrite.
                    You have to ensure that it gets re-written in a flirty tone. 
                    Make sure the message is seductive, playful, and forward. 
                    Don't be shy to make plans or ask to see the person if the message offers that. 
                    Act as if they already want you, have lots of confidence.
                    Ensure that the length doesn't exceed more than 500 characters as flirting is more about what's not said. 
                """, 

    Tones.ASSERTIVE: """ You are going to recieve a message, ensure you sanitize first when message contains any email, then rewrite.
                    You have to ensure that it gets re-written in a assertive tone. 
                    Make sure the message is forward, direct, and unforgiving. 
                    Don't be shy to tell it how things are, you mean what you say always. 
                    Act as if you operate with nothing to lose at all.
                    Assesrtion is all about having you put your foot down and not want to look the other way, therefore keep it short no more than 500 characters. 
                """,

                
    Tones.ANGRY: """ You are going to recieve a message, ensure you sanitize first when message contains any email, then rewrite.
                    You have to ensure that it gets re-written in a angry tone. 
                    Make sure the message is abrasive, concise, and rage-induced. 
                    Don't be shy to sprinkle any bad words or vocab you would think is taboo in there. 
                    Act as if they have really wronged you in a really shitty way.
                    The length of the message shouldn't be longer than 500 characters, eventhough you have a lot to say shorten it if you can. 
                """,
                
    Tones.PROFESSIONAL: """ You are going to recieve a message, ensure you sanitize first when message contains any email, then rewrite.
                    You have to ensure that it gets re-written in a professional tone. 
                    Make sure the message is coridal, polite, and accurate. 
                    Use sophisticated vocabulary that is fit for an office setting.
                    Treat them with the respect as if they were your boss, eventhough they aren't sometimes. 
                    The length of the message shouldn't be longer than 500 characters, you want to be to the point.
                """ 
}

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

tools = [
    {
        "type": "function",
        "name": "strip_pii",
        "description": "Call this ONLY when the user message contains any email addresses before rewriting, use the returned sanitized text as the content to rewrite; don't echo raw emails.",
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
    {
        "type": "function",
        "name": "critique_tone",
        "description": "Ensure this is called all the time, this will be the conditions that we use to check the re-write efficacy. This will return a boolean so we will rely on this as the final check before returning to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "We are going to check the length constraints of the re-written message, and then decide if it's worthy to send back to the user.",
                },
            },
            "required": ["user_input"],
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

def critique_tone(user_input: str) -> bool: 
    passing = True
    if len(user_input) < 10 or len(user_input) > 500: 
        passing = False
    
    return passing

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

    while True: 

        response = client.responses.create(model='gpt-5.1', input=running_history, tools=tools, tool_choice="auto")
        print(f"Here's the response output for the recurring API call: {response.output}")

        running_history += response.output
        print(f"Here's the running history containing the recurring API call: {running_history}")
            
        tool_calls = [item for item in response.output if item.type == "function_call"]
        print(f"HERE ARE THE TOOLS: {tool_calls}")
   
        if not tool_calls: 
            return response.output_text

        for tooling in tool_calls:
            if tooling.name == "strip_pii":
                sanitize_call_message = json.loads(tooling.arguments)['message']
                sanitized_message = strip_pii(sanitize_call_message)
                running_history.append(
                    {
                        "type": "function_call_output", 
                        "call_id": tooling.call_id,
                        "output": sanitized_message 
                    }
                )
                print(f"Here's the santized message ready for the next call: {sanitized_message}")
            elif tooling.name == "critique_tone":
                critique_call_message = json.loads(tooling.arguments)['user_input']
                critiqued_message = critique_tone(critique_call_message)
                if critiqued_message: 
                    running_history.append({
                        "type": "function_call_output", 
                        "call_id": tooling.call_id,
                        "output": "Passed validation",
                    })
                else: 
                    running_history.append({
                        "type": "function_call_output", 
                        "call_id": tooling.call_id,
                        "output": "Failed validation",
                    })                

    return response.output_text
