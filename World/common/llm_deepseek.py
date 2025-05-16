import tiktoken
from ollama import chat
from joblib import Memory
# from transformers import LlamaTokenizer  # type: ignore
# from transformers import AutoTokenizer
from pdb import set_trace as st
memory = Memory('cachedir', verbose=0)


deepseek_map = {"deepseek-r1:7b" : "deepseek-ai/deepseek-llm-7b",
                "deepseek-r1:14b" : "deepseek-ai/deepseek-llm-14b",
                "deepseek-r1:32b" : "deepseek-ai/deepseek-llm-32b",
                "deepseek-r1:70b" : "deepseek-ai/deepseek-llm-70b",
                }

def deepseek_llm(prompt, model_name, temperature=0.08, max_tokens=128, stop=None):
    messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
    # message = [{"role": "system", "content": intro}]
    # for (x, y) in examples:
    #     message.append(
    #         {
    #             "role": "system",
    #             "name": "example_user",
    #             "content": x,
    #         }
    #     )
    #     message.append(
    #         {
    #             "role": "system", #
    #             "name": "example_assistant",
    #             "content": y,
    #         }
    #     )
    # message.append({"role": "user", "content": current})
    response = chat(model=model_name, 
                    messages=messages,
                    options={'temperature': temperature, 
                            #  'top_p': 1,
                            #  'num_predict': 100*lm_config.gen_config["max_tokens"],} 
                            }
                    )
    message = response['message']['content']
    return message


# class Tokenizer(object):
#     def __init__(self, provider: str, model_name: str) -> None:
#         if provider == "openai":
#             self.tokenizer = tiktoken.encoding_for_model(model_name)
#         elif provider == "huggingface":
#             self.tokenizer = LlamaTokenizer.from_pretrained(model_name)
#             # turn off adding special tokens automatically
#             self.tokenizer.add_special_tokens = False  # type: ignore[attr-defined]
#             self.tokenizer.add_bos_token = False  # type: ignore[attr-defined]
#             self.tokenizer.add_eos_token = False  # type: ignore[attr-defined]
#         elif provider == 'deepseek':
#             # self.tokenizer = AutoTokenizer.from_pretrained(deepseek_map[model_name])
#             model_name = "deepseek-ai/DeepSeek-V2"
#             self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
#         else:
#             raise NotImplementedError

#     def encode(self, text: str) -> list[int]:
#         return self.tokenizer.encode(text)

#     def decode(self, ids: list[int]) -> str:
#         return self.tokenizer.decode(ids)

#     def __call__(self, text: str) -> list[int]:
#         return self.tokenizer.encode(text)