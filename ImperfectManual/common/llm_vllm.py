import tiktoken
# from openai import OpenAI
from joblib import Memory
# from transformers import LlamaTokenizer  # type: ignore
# from transformers import AutoTokenizer
from pdb import set_trace as st
memory = Memory('cachedir', verbose=0)

# client = OpenAI(
#     base_url="http://localhost:8080/v1",
#     api_key="EMPTY",
# )

def remove_think(content):
    return content.split('</think>')[-1]

def vllm_llm(prompt, model_name, temperature=0.08, max_tokens=128, stop=None):
    prompt = '/nothink ' + prompt # Do this unless you want a reasoning model
    messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature
    )
    message = completion.choices[0].message.content

    if 'Qwen3' in model_name:
        message = remove_think(message)

    return message