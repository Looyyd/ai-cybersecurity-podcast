import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt35_complete(prompt):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that creates podcast scripts."},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    return response.choices[0].message.content

# function that uses gpt4 to complete a prompt
def gpt4_complete(prompt):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that creates podcast scripts."},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation,
    )
    return response.choices[0].message.content
