import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt="Please give 3 synonyms of the word extraordinary."
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
]


response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=conversation,
)
print(response)