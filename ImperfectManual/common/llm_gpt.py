import os
import openai
# from openai import OpenAI
from joblib import Memory
from pdb import set_trace as st

# openai.api_key = os.environ["OPENAI_API_KEY"]
memory = Memory('cachedir', verbose=0)

# cache the result to avoid sending duplicate requests.
# @memory.cache
# def openai_llm(prompt, 
#                model_name, 
#                instruction,
#                temperature=0.08, max_tokens=128, stop=None):
#     # time.sleep(0.001 * token_num(prompt)) #let the program sleep a bit due to the potential rate limit.

#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#     response = client.responses.create(
#         model=model_name,
#         input=prompt,
#         instructions=instruction,
#         temperature=temperature,
#         max_output_tokens=max_tokens,
#         stop=stop,
#     )

#     return response.output_text

@memory.cache
def openai_llm(prompt, 
               model_name, 
               temperature=0.08, max_tokens=128, stop=None):
    # time.sleep(0.001 * token_num(prompt)) #let the program sleep a bit due to the potential rate limit.

    if model_name in ['o3-mini', 'o1']:
        messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
        response = openai.ChatCompletion.create(
            model=model_name,
            messages = messages,
            max_completion_tokens=20000, 
            stop=stop,
        )
        response_content = response["choices"][0]['message']['content']
    else:
        messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
        response = openai.ChatCompletion.create(
            model=model_name,
            messages = messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        response_content = response["choices"][0]['message']['content']
    return response_content
