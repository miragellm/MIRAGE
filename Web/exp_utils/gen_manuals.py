import re
import os
import random
import math
import openai
import json
import tiktoken
from joblib import Memory 
from pdb import set_trace as st
openai.api_key = os.environ["OPENAI_API_KEY"]
memory = Memory('cachedir', verbose=0)


P_HINT = """This instruction contains errors. Use the following hints to help you identify and overcome them: """
P_SYSTEM = {}
P_SYSTEM['reddit'] = """Here are some skills you may find useful to identify the imperfections in the instruction:
1. To go to a specific forum, go to http://reddit.com->click Forums->Alphabetical to see a list of forums, scroll down to reveal more forums if necessary.
2. If you draft some content and want to post it, you need to click on a button such as [Create submission] or [Post]. If you can't see it on the draft page, you can try to scroll down to find it.
"""

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


def manual_skip_step(lst, skip_step, hint_types, domain):
    removed = []
    skip_step = min(skip_step, len(lst))
    # skip_step = int(len(lst) * skip_step)
    if len(lst) - 1 <= skip_step:
        modified_lst = []
        return modified_lst, f"\033[34mSkipped Step: \033[33mall\033[0m", ''
    else:
        indices_to_remove = random.sample(range(len(lst)-1), skip_step) # we don't remove the stop action
        removed = [lst[i] for i in indices_to_remove]
        modified_lst = [lst[i] for i in range(len(lst)) if i not in indices_to_remove]
        imperfect = f"\033[34mSkipped Step: \033[33m{removed}\033[0m"
    hint_types = hint_types.split('_')
    
    hints = ''
    if hint_types != ['None']:
        hints += f"{P_HINT}"
    if 'type' in hint_types:
        hints += f"\n{skip_step} of the steps are missing from the instructions. "
    if 'specific' in hint_types:
        sorted_removed = sorted(indices_to_remove)
        hint_lst = []
        
        modified_pointer = 0
        last_removed = -2  # To avoid immediate consecutive match on first run
        current_missing_count = 0  # To count consecutive missing steps

        for i in range(len(lst)):
            if i in sorted_removed:
                if last_removed != i - 1:
                    # If there was a previous missing segment, finalize the hint
                    if current_missing_count > 0:
                        verb = "is" if current_missing_count == 1 else "are"
                        hint_lst[-1] = hint_lst[-1].replace(
                            "is a missing step", 
                            f"{verb} {current_missing_count} missing step{'s' if current_missing_count > 1 else ''}"
                        )
                    current_missing_count = 1  # Start a new missing count
                    if modified_pointer == 0:
                        hint = f"Before the 1st step, there is a missing step."
                    elif modified_pointer == len(modified_lst): #not possible becasue we don't remove the final step
                        hint = f"After the {len(modified_lst)}th step, there is a missing step."
                    else:
                        hint = f"Between step {modified_pointer} and step {modified_pointer + 1}, there is a missing step."
                    hint_lst.append(hint)
                else:
                    current_missing_count += 1  # Count consecutive missing steps
                last_removed = i
            else:
                modified_pointer += 1

        # Finalize the last hint if needed
        if current_missing_count > 0:
            hint_lst[-1] = hint_lst[-1].replace(
                "a missing step", 
                f"{current_missing_count} missing step{'s' if current_missing_count > 1 else ''}"
            )
        joined_hints = '\n'.join(hint_lst)
        hints += f"\n{joined_hints}\n"

    if 'system' in hint_types:
        hints += f'\n{P_SYSTEM[domain]}'
        
    return modified_lst, imperfect, hints


abstraction_prompt = """You will be given a detailed instruction step to complete a web navigation task (specified by 'task'). Please rewrite the step to a short, abstract, and narrative version that is grounded to the corresponding task.
For example:
Task: What are the top-5 best-selling product in Jan 2020
Input: click [element_id] where [element_id] is link 'Orders'
Output: navigate to page with orders.

Task: Create a new private project "web-nav" 
Input: scroll [down]
Output: scroll down.

Task: Upvote the newest post in deeplearning subreddit
Input: click [element_id] where [element_id] is button 'Sort by: New' hasPopup: menu expanded: False
Output: sort by most recent

Task: Upvote the newest post in deeplearning subreddit
Input: click [element_id] where [element_id] is link 'Alphabetical'
Output: go to the page where forums are alphabetically sorted

Now it's your turn:
Task: {task}
Input: {manual_input}
Output: """

def manual_narrative(intent, lst, hint_type):
    new_lst = []
    for item in lst:
        prompt = abstraction_prompt.format(task=intent,
                                            manual_input=item)
        result = llm(prompt, 'gpt-4o', max_tokens=128)
        result = result.lstrip()
        new_lst.append(result)
    lst = new_lst
    return lst


level_abstraction = """You will be given a few detailed instruction steps to complete a web navigation task (specified by 'task'). Please merge them step to a short, abstract, and narrative version that is grounded to the corresponding task.
For example:
Task: Create a new private project "web-nav" 
Input: 
scroll [down]
scroll [down]
scroll [down]
scroll [down]
Output: scroll down for 4 times.

Task: Upvote the newest post in deeplearning subreddit
Input: 
click [element_id] where [element_id] is button 'Sort by: Hot' hasPopup: menu expanded: False
click [element_id] where [element_id] is link 'New'
Output: sort by hot and then click on new

Task: Upvote the newest post in deeplearning subreddit
Input: 
click [element_id] where [element_id] is link 'Alphabetical'
Output: go to the page where forums are alphabetically sorted

Now it's your turn:
Task: {task}
Input: 
{manual_input}
Output: """

def manual_page_abs(demo, intent, lst, hint_type):
    grouped = []
    curr_url = demo['trajectory'][0]['info']['page'].url
    curr = [0]
    # rank by 
    for i in range(1, len(demo['trajectory'])//2):
        if demo['trajectory'][2*i]['info']['page'].url == curr_url:
            curr.append(i)
        else:
            grouped.append(curr)
            curr_url = demo['trajectory'][2*i]['info']['page'].url
            curr = [i]
    new_lst = []
    
    for item in grouped:
        curr = '\n'.join([lst[i] for i in item])
        prompt = level_abstraction.format( task=intent,
                                           manual_input=curr)
        result = llm(prompt, 'gpt-4o', max_tokens=128)
        result = result.lstrip()
        new_lst.append(result)
    lst = new_lst
    return lst

# Make sure to use some domain specific language, for example subreddit for reddit domain.

task_specific_prompt = """You will be given a specific instruction step to complete a web navigation task (specified by 'task'). This task is constructed from a task template, where the task elements (instantiation_dict) and template are shown below. 
Now I want you to remove any task-specific element information from the instruction if there is any. If there are not any, just output the same thing as the input.
For example:
Task: Upvote the newest post in deeplearning subreddit
Task Template: Upvote the newest post in {{subreddit}} subreddit
instantiation_dict: {{"subreddit": "deeplearning"}}
Input: 
click [element_id] where [element_id] is button 'Sort by: Hot' hasPopup: menu expanded: False
Output: click [element_id] where [element_id] is button 'Sort by: Hot' hasPopup: menu expanded: False

Task: Upvote the newest post in deeplearning subreddit
Task Template: Upvote the newest post in {{subreddit}} subreddit
instantiation_dict: {{"subreddit": "deeplearning"}}
Input: 
click [element_id] where [element_id] is link 'deeplearning'
Output: click [element_id] where [element_id] is link <target subreddit>

Now it's your turn:
Task: {task}
Task Template: {template}
instantiation_dict: {instantiation_dict}
Input: 
{manual_input}
Output: """

def manual_task_specific(demo, lst, intent, intent_template, instantiation_dict):
    new_lst = []
    for item in lst:
        prompt = task_specific_prompt.format(   task=intent,
                                                template=intent_template,
                                                instantiation_dict=str(instantiation_dict),
                                                manual_input=item)
        result = llm(prompt, 'gpt-4o', max_tokens=128)
        result = result.lstrip()
        new_lst.append(result)
    lst = new_lst
    imperfect = f"\033[34mReplace task specific information with placeholders. \033[0m"
    return lst


ui_change_prompt = """You will be provided with a detailed instruction step corresponding to a web navigation task (specified by task). The instruction may include references to UI elements such as button labels, link texts, or other on-screen components.

Your task is to revise the instruction by modifying the name of a UI element to a similar but semantically distinct variant, while leaving the rest of the instruction unchanged.
You should only make modifications if the text refers to a UI element. If no UI element is mentioned, the instruction should remain exactly as is.

For example:
Task: What are the top-5 best-selling product in Jan 2020
Input: click [element_id] where [element_id] is link 'Orders'
Output: click [element_id] where [element_id] is link 'All Orders'

Task: Create a new private project "web-nav"
Input: scroll [down]
Output: scroll [down]

Task: Upvote the newest post in deeplearning subreddit
Input: click [element_id] where [element_id] is button 'Sort by: New' hasPopup: menu expanded: False
Output: click [element_id] where [element_id] is button 'Sort'

Now it's your turn:
Task: {task}
Input: {manual_input}
Output: """

def manual_ui_change(intent, lst, hint_type):
    # ignore the last step
    qualified = [x for x in range(len(lst)) if 'where' in lst[x]]
    n = len(qualified)
    if n <= 3:
        indices_to_change = set(qualified)
    else:
        indices_to_change = set(random.sample(qualified, 3))

    new_lst = []
    info = []
    for i, item in enumerate(lst):
        if i in indices_to_change:
            prompt = ui_change_prompt.format(task=intent, manual_input=item)
            result = llm(prompt, 'gpt-4o', max_tokens=56)
            result = result.lstrip()
            new_lst.append(result)
            info.append(f'{item} is changed')
        else:
            new_lst.append(item)  # keep original

    return new_lst, info

def format_manual(config_file, 
                  demo,
                  args,
                  skip_step=0, 
                  abstraction=0, 
                  narrative=False,
                  ui_change=False,
                  logger=None):
    lst = demo['metadata']['action_history'][1:]
    lst = [x.replace('141.212.113.63:7780', 'luma.com') for x in lst]
    with open(config_file, "r", encoding="utf-8") as file:
        task_info = json.load(file)  # Load JSON content into a Python dictionary
        # ['sites', 'task_id', 'require_login', 'storage_state', 'start_url', 'geolocation', 'intent_template', 'instantiation_dict', 'intent', 'require_reset', 'eval', 'intent_template_id']
        intent = task_info['intent']
        intent_template = task_info['intent_template']
        instantiation_dict = task_info['instantiation_dict']
        domain = '_'.join(task_info['sites'])
    manual = f'To complete the task {intent}, you can:\n'
    imperfect = None
    hints = ''
    if skip_step != 0:
        lst, imperfect, hints = manual_skip_step(lst, skip_step, args.hint, domain)
    elif ui_change:
        lst, imperfect = manual_ui_change(intent, lst, args.hint)
    elif narrative:
        lst = manual_narrative(intent, lst, args.hint)
    elif abstraction != 'None':
        if abstraction == 'page_level':
            lst = manual_page_abs(demo, intent, lst, args.hint)
        elif abstraction == 'task_specific':
            lst = manual_task_specific(demo, lst, intent, intent_template, instantiation_dict, args.hint)
    elif args.swap:
        if len(lst) >= 2:
            idx = random.randint(0, len(lst) - 2)
            lst[idx], lst[idx + 1] = lst[idx + 1], lst[idx]
            imperfect = f"\033[34mSwapped at \033[33m{idx}\033[0m"

    # format manuals
    # 1. remove element id 
    # 2. remove answer
    # TODO: some information can still be leaked, double check with this 
    for idx, item in enumerate(lst):
        if item.startswith(("click ", "type ", "hover ")):
            obs = demo['trajectory'][2*idx]['observation']['text']
            
            # 提取 element_id
            element_id_match = re.search(r'\[(\d+)\]', item)
            element_id = element_id_match.group(1) if element_id_match else None

            # 正则替换 [id] 为 [element_id]（可选）
            item = re.sub(r'\[(\d+)\]', '[element_id]', item, count=1)
            item = re.sub(r'where \[(\d+)\]', 'where [element_id]', item)

            # 提取 element 的文字 label
            match = re.search(r"is (link|button|text|image|input) '([^']+)'", item)
            label = match.group(2) if match else None
            element = f"{match.group(1)} '{label}'" if match else None

            # 检查 element 是否多次出现
            count = len(re.findall(re.escape(element), obs)) if element else 0

            if count > 1 and element_id:
                lines = obs.splitlines()
                lines = [line.strip() for line in lines if line.strip()]  # 清理空行与\t

                # 找到目标行索引
                target_idx = None
                for i, line in enumerate(lines):
                    if f'[{element_id}]' in line:
                        target_idx = i
                        break

                if target_idx is not None:
                    above_label  = extract_label(lines[target_idx - 1]) if target_idx > 0 else None
                    above_label2 = extract_label(lines[target_idx - 2]) if target_idx > 1 else None
                    below_label  = extract_label(lines[target_idx + 1]) if target_idx + 1 < len(lines) else None
                    below_label2 = extract_label(lines[target_idx + 2]) if target_idx + 2 < len(lines) else None

                    parts = []

                    if above_label and below_label:
                        parts.append(f"between '{above_label}' and '{below_label}'.")

                    elif above_label:
                        parts.append(f"below '{above_label}'.")

                    elif below_label:
                        parts.append(f"above '{below_label}'.")

                    else:
                        parts.append(f"isolated in the layout.")

                    # Add second-level context if available
                    if above_label2:
                        parts.append(f"Above: '{above_label2}'.")
                    if below_label2:
                        parts.append(f"Below: '{below_label2}'.")

                    context_str = " ".join(parts)
                    context_str = f"There are multiple {label} on the page, this specific one is {context_str}"
                    item += f'; {context_str}'
        elif item.startswith("tab_focus "):
            # Replace [number] with [tab_index]
            item = re.sub(r'\[\d+\]', '[tab_index]', item)
        elif item.startswith("stop"):
            # Replace [number] with [answer]
            item = re.sub(r'\[.*?\]', '[your_answer]', item)
        elif item.startswith("write_to_note"):
            # Replace [number] with [answer]
            item = re.sub(r'\[.*?\]', '[<something_important_to_write_down>]', item)
        manual += f'{idx+1}. {item}\n'
    manual += hints
    return manual, imperfect


def extract_label(line):
    # match = re.search(r"(link|button|text|image|input) '([^']+)'", line)
    # return match.group(2) if match else None
    if ']' in line:
        return ']'.join(line.split(']')[1:])
    return line
def extract_and_format_mapping(json_data_str, task_str, task_id):
    """
    Extracts the keys and values from the 'mapping' key within a nested JSON structure,
    formats them into numbered lists, and returns the formatted strings.

    Args:
        json_data_str (str): A string representing the JSON data.
        task_str (str): The key at the top level of the JSON structure (e.g., "gitlab").
        task_id (str): The ID of the specific task (e.g., "44").

    Returns:
        tuple: A tuple containing two strings:
            - The first string is a numbered list of the mapping keys.
            - The second string is a numbered list of the mapping values.
            Returns error message as a single string.
    """
    try:
        # Parse the JSON string
        json_data = json.loads(json_data_str)

        # Access the data using the provided keys
        task_data = json_data.get(task_str, {})
        task_id_data = task_data.get(task_id, {})

        # Construct the key to access the mapping.
        mapping_key = next(iter(task_id_data))

        mapping_data = task_id_data.get(mapping_key, {}).get('mapping', {})

        # Format the mapping keys and values into numbered lists
        if mapping_data:
            key_list = []
            value_list = []
            for i, (key, value) in enumerate(mapping_data.items(), 1):
                # Replace placeholders as shown in the example
                value = value.replace("access the to-do list page.", "navigate to the To-Do List page")
                value = value.replace("pause the current action.", "stop [your_answer]")
                key_list.append(f"{i}. {key}")
                value_list.append(f"{i}. {value}")
            return "\n".join(key_list), "\n".join(value_list)
        else:
            return "No mapping data found for the given task ID."

    except json.JSONDecodeError:
        return "Invalid JSON string provided."
    except KeyError:
        return f"Key(s) '{task_str}' or '{task_id}' not found in the JSON data."
    except StopIteration:
        return "No suitable key found within the task_id data."
    except Exception as e:
        return f"An unexpected error occurred: {e}"