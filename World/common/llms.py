import os
import time
import openai
import signal
import tiktoken
from joblib import Memory
from common.utils import error_handle
from .llm_gpt import openai_llm
# from .llm_deepseek import deepseek_llm
from .llm_ollama import ollama_llm
#from .llm_vllm import vllm_llm
from pdb import set_trace as st

openai.api_key = os.environ["OPENAI_API_KEY"]
memory = Memory('cachedir', verbose=0)

def token_num(prompt):
    # return the number of token in a prompt.
    encoder = tiktoken.get_encoding("cl100k_base")
    if isinstance(prompt, str):
        token_num = len(encoder.encode(prompt))
    elif isinstance(prompt, list):
        token_num = 0
        for message in prompt:
            token_num += len(message['role'])
            token_num += len(message['content'])
    return token_num

def truncate(prompt, max_token):
    encoder = tiktoken.get_encoding("cl100k_base")
    return encoder.decode(encoder.encode(prompt)[:max_token])

def print_info(logger, msg):
    if logger:
        logger.log(msg, option='print')
    else:
        print(msg)
        
        
TOKEN_LIMITS = {'gpt-4-turbo-2024-04-09': 128000,
                'gpt-4-turbo': 128000,
                'gpt-4o': 128000,
                'gpt-4o-mini': 128000,
                'gpt-4-0125-preview': 128000,
                'gpt-4-turbo-preview': 128000,
                'gpt-3.5-turbo-0125': 16385,
                'gpt-3.5-turbo-0613': 16385,
                'gpt-3.5-turbo': 16385,
                'gpt-3.5-turbo-instruct': 4096}

ollama_models = ['qwen3:32b', 'llama3:70b', 'qwen3:235b', 'llama3.3:70b', 'qwen3:14b', 'gemma3:12b']
vllm_models = ['Qwen/Qwen3-32B']

def llm(prompt, 
        model_name, 
        temperature=0.08, 
        max_tokens=128, 
        stop=None,
        logger=None,
        max_trial=10,
        reset_context=False,
        ):
    """
    token_size = token_num(prompt)
    try:
        token_limit = int(0.9 * TOKEN_LIMITS[model_name]) 
    except Exception as e:
        # print(f"\033[31mWARNING:\033[0m:\nPlease add token limit for the model you use in common/llms.py TOKEN_LIMITS={TOKEN_LIMITS}.\n")
        token_limit = 128000

    if token_size > token_limit:
        prompt = prompt[-token_limit:]
        print_info(logger, f"\033[31mWARNING\033[0m:The prompt is truncated because it exceeds the token limit.\n")
    """
 

    # set a time limit to retry, please use it wisely.
    budget = max_trial
    response_content = ''
    while budget > 0:
        try:
            signal.signal(signal.SIGALRM, error_handle) 
            signal.alarm(5000) # wait for at most 300s for one openai call (maybe it's too long, can change it per your choice)
            if model_name in vllm_models:
                response_content = vllm_llm(prompt, model_name, temperature, max_tokens, stop)
            elif model_name in ollama_models:
                response_content = ollama_llm(prompt, model_name, temperature, max_tokens, stop)
            else:
                response_content = openai_llm(prompt,
                                              model_name, 
                                            #   instruction='You are an intelligent assistant helping to complete a multi-step task.',
                                              temperature=temperature, 
                                              max_tokens=max_tokens, 
                                              stop=stop)
            budget = 0
        except Exception as e:
            print_info(logger, f"\033[31mError\033[0m:{e}. LLM not responding, redoing the task now...")
            budget -= 1

    return response_content

def print_prompt(prompt):
    if isinstance(prompt, str):
        print(f"\033[34mPrompt\033[0m:prompt")
    elif isinstance(prompt, list):
        for message in prompt:
            print(f"\033[34m{message['role']}\033[0m:\n{message['content']}\n")