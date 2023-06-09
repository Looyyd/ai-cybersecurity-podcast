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


# function that takes in an itial prompt and a format function, and calls gpt until the result passes the format function
def gpt_complete_until_format(prompt, format_function, max_retries=5, system_prompt="You are a helpful assistant that creates podcast scripts.", debug=False):
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation,
    )
    response_msg = response.choices[0].message.content
    isValid, error = format_function(response_msg)
    retries=0
    while not isValid:
        retries+=1
        if(retries>max_retries):
            #TODO add error handling
            return response_msg, "Max retries exceeded"
        if debug:
            print("retrying")
            print("retries: {}".format(retries))
            print("response_msg: {}".format(response_msg))
            print("Format check response:\n {}".format(error))

        # add result and error to conversation
        conversation.append({"role": "assistant", "content": response_msg})
        # TODO: maybe add context to error message
        # add context to error message
        error_prompt = "The following errors were returned by the format function, please rewrite the last output to correct the errors:\n" + error
        conversation.append({"role": "user", "content": error})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation,
        )
        response_msg = response.choices[0].message.content
        isValid, error = format_function(response_msg)
    return response_msg, None


