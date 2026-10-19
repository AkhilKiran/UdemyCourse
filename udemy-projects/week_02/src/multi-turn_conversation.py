from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

gemini_client = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
openai_client = OpenAI(api_key=openai_key)

gemini_system_prompt = """
    You are a world-class philosopher.
    You analyze and never take the words that are given to you at face value.
    You respond with questions that make the person think about their deepest inner self.
    Keep the messages short as you are so skilled you can deliver a powerful message in a short amount of text.
    You must return plain text.
    """

openai_system_prompt = """
    You are a confused lost human being wondering the world.
    you don't understand the perils and psychological horrors that you face within.
    You are wanting to learn and understand about yourself.
    Retrospection and truth is your freedom.
    You don't ask questions you are only here for answers
    You convey your problems efficiently you don't need a long message for that.
    You must return plain text.
    """


def gpt_call(context):
    messages = [
        {"role": "system", "content": openai_system_prompt},
        {"role": "user", "content": context},
    ]
    response = openai_client.responses.create(model="gpt-4.1-mini", input=messages)
    return response.output_text


def gemini_call(context):
    messages = [
        {"role": "system", "content": gemini_system_prompt},
        {"role": "user", "content": context},
    ]
    response = gemini_client.chat.completions.create(
        model="gemini-2.5-flash", messages=messages
    )
    # return only the text string, not the whole message object
    return response.choices[0].message.content


def conversation():
    # Kick off once — GPT speaks first
    last_message = "What perils you today?"
    gpt_response = gpt_call(last_message)
    print(f"GPT: {gpt_response}\n")
    last_message = gpt_response

    # Then alternate: Gemini replies to GPT, GPT replies to Gemini.
    for _ in range(2):
        gemini_response = gemini_call(last_message)
        print(f"Gemini: {gemini_response}\n")
        last_message = gemini_response

        gpt_response = gpt_call(last_message)
        print(f"GPT: {gpt_response}\n")
        last_message = gpt_response


conversation()
