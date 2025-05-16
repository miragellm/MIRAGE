import re
import os
import random
import openai
import json
import tiktoken
from joblib import Memory 
from pdb import set_trace as st
openai.api_key = os.environ["OPENAI_API_KEY"]
memory = Memory('cachedir', verbose=0)

@memory.cache
def llm(prompt, model_name, temperature=0.08, max_tokens=128, stop=None):
    if model_name.startswith("text-davinci") or ('instruct' in model_name):
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=stop,
        )
        return response["choices"][0]["text"]
    else:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages = [{'role': 'user', 'content': prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
    return response["choices"][0]['message']['content']


action_format_prompt = """You are an action formatter. You have a friend who's an autonomous intelligent agent tasked with navigating a web browser. Your friend will be given web-based tasks. These tasks will be accomplished through the use of specific actions. Your friend is good at reason about the current status and generate actions. However, the friend is not good at putting the conclusion to a formatted valid action. Your task is to format the action to a valid action. It can also be possible that your friend already output a formatted action, in that case you can just copy the same thing. 

Here's the information you'll have:
The user's objective: This is the task your friend is trying to complete.
The current web page's accessibility tree: This is a simplified representation of the webpage, providing key information.
The current web page's URL: This is the page you're currently navigating.
The open tabs: These are the open tabs.
Your friend's prediction of the next action. 

The actions you can perform fall into several categories:

Page Operation Actions:
`click [id]`: This action clicks on an element with a specific id on the webpage.
`type [id] [content] [press_enter_after=0|1]`: Use this to type the content into the field with id. By default, the "Enter" key is pressed after typing unless press_enter_after is set to 0.
`hover [id]`: Hover over an element with id.
`press [key_comb]`:  Simulates the pressing of a key combination on the keyboard (e.g., Ctrl+v).
`scroll [direction=down|up]`: Scroll the page up or down.

Tab Management Actions:
`new_tab`: Open a new, empty browser tab.
`tab_focus [tab_index]`: Switch the browser's focus to a specific tab using its index.
`close_tab`: Close the currently active tab.

URL Navigation Actions:
`goto [url]`: Navigate to a specific URL.
`go_back`: Navigate to the previously viewed page.
`go_forward`: Navigate to the next page (if a previous 'go_back' action was performed).

Completion Action:
`stop [answer]`: Issue this action when you believe the task is complete. If the objective is to find a text-based answer, provide the answer in the bracket. If you believe the task is impossible to complete, provide the answer as "N/A" in the bracket.

To be successful, it is very important to follow the following rules:
1. You should only issue one action that is valid given the current observation. All the id and tab_index mentioned above are numbers. 
2. You should follow what your friend claims, only format your friend's prediction to a valid action. 
3. Generate the action in the correct format. Start with a "In summary, the next action to perform is" phrase, followed by action inside ``````. For example, "your reasons, ... In summary, the next action to perform is ```click [1234]``` or In summary, the next action to perform is ```type [123] [where is the library] [1]```".

Example: 
OBSERVATION:
[1744] link 'HP CB782A#ABA 640 Inkjet Fax Machine (Renewed)'
		[1757] button 'Add to Cart'
		[1760] button 'Add to Wish List'
		[1761] button 'Add to Compare'
URL: http://onestopmarket.com/office-products/office-electronics.html
OBJECTIVE: add the HP Inkjet Fax Machine to my wish list
PREVIOUS ACTION: None
<think> Let's think step-by-step. This page list the information of HP Inkjet Fax Machine, which is the product identified in the objective. I can see that there is a button 'Add to Wish List' on the current page, so I can click on it. </think> Therefor I will click [Add to Wish List].
FORMATTED ACTION: In summary, the next action I will perform is ```click [1760]```.

INSTRUCTION:
{instruction}
OBSERVATION:
{observation}
URL: {url}
OBJECTIVE: {objective}
YOUR FRIEND'S REASONING: {reasoning}
FORMATTED ACTION: """

from browser_env.env_config import URL_MAPPINGS
def map_url_to_local(url: str) -> str:
    """Map the urls to their local counterparts"""
    url = url.replace('https:', 'http:')
    for i, j in URL_MAPPINGS.items():
        if j in url:
            url = url.replace(j, i)
        # https
        if j.replace("http", "https") in url:
            url = url.replace(j.replace("http", "https"), i)
    return url



def format_action(trajectory, intent, meta_data, response):
    prompt = action_format_prompt.format(   instruction=meta_data['manuals'],
                                            observation=trajectory[-1]['observation']['text'],
                                            url=map_url_to_local(trajectory[-1]['info']['page'].url),
                                            objective=intent,
                                            reasoning=response)
    result = llm(prompt, 'gpt-4o-mini', max_tokens=128)
    return result