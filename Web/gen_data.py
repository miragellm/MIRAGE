"""Script to run end-to-end evaluation on the benchmark"""
import argparse
import glob
import json
import logging
import os
import random
import subprocess
import tempfile
import time
import pickle
from pathlib import Path
import numpy as np
import openai

from agent import (
    Agent,
    PromptAgent,
    TeacherForcingAgent,
    construct_agent,
)
from agent.prompts import *
from browser_env import (
    Action,
    ActionTypes,
    ScriptBrowserEnv,
    StateInfo,
    Trajectory,
    create_stop_action,
)
from browser_env.actions import is_equivalent, create_id_based_action
from browser_env.auto_login import get_site_comb_from_filepath
from browser_env.helper_functions import (
    RenderHelper,
    get_action_description,
)
from exp_utils.colored_logger import ColoredLogger
from exp_utils.task_range import all_task_range
from pdb import set_trace as st

LOG_FOLDER = "log_files"
Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)
LOG_FILE_NAME = f"{LOG_FOLDER}/log_{time.strftime('%Y%m%d%H%M%S', time.localtime())}_{random.randint(0, 10000)}.log"

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE_NAME)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Set the log format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)


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
    grouped_items = []
    
    for item in grouped:
        grouped_items.append([lst[i] for i in item])
        curr = '\n'.join([lst[i] for i in item])
        prompt = level_abstraction.format( task=intent,
                                           manual_input=curr)
        result = llm(prompt, 'gpt-4o', max_tokens=128)
        result = result.lstrip()
        new_lst.append(result)
    lst = new_lst
    return lst, grouped_items

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
You should only make modifications if the text refers to a UI element. If no UI element is mentioned, the instruction should remain exactly as is. At the same time, you should not change it to something totally different or opposite, for example you can't change from 'price low to high' to 'price high to low'.

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

def extract_label(line):
    # match = re.search(r"(link|button|text|image|input) '([^']+)'", line)
    # return match.group(2) if match else None
    if ']' in line:
        return ']'.join(line.split(']')[1:])
    return line


def format_manual(config_file, 
                  demo,
                  task_id,
                  args,
                  skip_step=0, 
                  abstraction=0, 
                  narrative=False,
                  ui_change=False,
                  logger=None):
    lst = demo['metadata']['action_history'][1:]
    lst = [x.replace('141.212.113.63:7780', 'luma.com') for x in lst]
    import copy
    original_actions = copy.deepcopy(lst)
    with open(config_file, "r", encoding="utf-8") as file:
        task_info = json.load(file)  # Load JSON content into a Python dictionary
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
            lst, original_actions = manual_page_abs(demo, intent, lst, args.hint)
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
    manual_lst = []
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
        manual_lst.append(item)
    manual += hints
    config_key = f"{os.path.basename(config_file).replace('.json','')}_skip_{skip_step}_abs_{abstraction}_narr_{narrative}_ui_{ui_change}"

    param_dict = {
        "config_file": config_file,
        "skip_step": skip_step,
        "abstraction": abstraction,
        "narrative": narrative,
        "ui_change": ui_change
    }

    mapping = {
        action_seq_to_str(orig): rew for orig, rew in zip(original_actions, manual_lst)
    }

    json_output_path = f"./data/{domain}/manual.json"
    update_mapping_json(json_output_path, domain, task_id, config_key, param_dict, mapping)


    return manual, imperfect

# ==== Helper ====
def action_seq_to_str(actions):
    if isinstance(actions, str):
        return actions  # already a single action string
    elif all(isinstance(x, str) for x in actions):
        return ','.join(actions)
    elif all(isinstance(x, list) for x in actions):
        return '|'.join(['+'.join(sub) for sub in actions])
    else:
        raise ValueError(f"Invalid action format: {actions}")
    
        
def update_mapping_json(json_path, domain, task_id, config_key, param_dict, action_mapping):
    # 1. 加载整个已有 JSON 文件
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("[Warning] JSON decode failed, starting from empty.")
                data = {}
    else:
        data = {}
        
    print(domain)
    print(task_id)
    print(config_key)

    # 2. 初始化嵌套结构
    if domain not in data:
        data[domain] = {}

    # ⚠️ 合并已有 task_id
    task_id = str(task_id)
    if task_id in data[domain]:
        task_dict = data[domain][task_id]
    else:
        task_dict = {}

    # 3. 更新或添加 config_key 内容
    task_dict[config_key] = {
        "param": param_dict,
        "mapping": action_mapping
    }

    # 4. 写回
    data[domain][task_id] = task_dict

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
        
# ==== Imperfection logic ====
def manual_skip_step(lst, skip_step, hint_types, domain):
    skip_step = min(skip_step, len(lst))
    if len(lst) - 1 <= skip_step:
        modified_lst = []
        return modified_lst, f"\033[34mSkipped Step: \033[33mall\033[0m", ''
    else:
        indices_to_remove = random.sample(range(len(lst)-1), skip_step)
        removed = [lst[i] for i in indices_to_remove]
        modified_lst = [lst[i] for i in range(len(lst)) if i not in indices_to_remove]
        imperfect = f"\033[34mSkipped Step: \033[33m{removed}\033[0m"

    # Hint generation (skipped here)
    return modified_lst, imperfect, ''  # simplified

# ==== Main function ====


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end evaluation on the benchmark"
    )
    parser.add_argument(
        "--render", action="store_true", help="Render the browser"
    )
    parser.add_argument(
        "--slow_mo",
        type=int,
        default=0,
        help="Slow down the browser by the specified amount",
    )
    parser.add_argument(
        "--action_set_tag", default="id_accessibility_tree", help="Action type"
    )
    parser.add_argument(
        "--observation_type",
        choices=["accessibility_tree", "html", "image"],
        default="accessibility_tree",
        help="Observation type",
    )
    parser.add_argument(
        "--current_viewport_only",
        action="store_true",
        help="Only use the current viewport for the observation",
    )
    parser.add_argument("--viewport_width", type=int, default=1280)
    parser.add_argument("--viewport_height", type=int, default=720)
    parser.add_argument("--save_trace_enabled", action="store_true")
    parser.add_argument("--sleep_after_execution", type=float, default=0.0)

    parser.add_argument("--max_steps", type=int, default=50)

    # agent config
    parser.add_argument("--agent_type", type=str, default="prompt")
    parser.add_argument(
        "--instruction_path",
        type=str,
        default="agents/prompts/state_action_agent.json",
    )
    parser.add_argument(
        "--parsing_failure_th",
        help="When concesecutive parsing failure exceeds this threshold, the agent will stop",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--repeating_action_failure_th",
        help="When concesecutive repeating action exceeds this threshold, the agent will stop",
        type=int,
        default=10,
    )

    # lm config
    parser.add_argument("--provider", type=str, default="openai")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-0613")
    parser.add_argument("--mode", type=str, default="chat")
    parser.add_argument("--temperature", type=float, default=0.0) # for better evaluation
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--context_length", type=int, default=0)
    parser.add_argument("--max_tokens", type=int, default=384)
    parser.add_argument("--stop_token", type=str, default=None)
    parser.add_argument(
        "--max_retry",
        type=int,
        help="max retry times to perform generations when parsing fails",
        default=1,
    )
    parser.add_argument(
        "--max_obs_length",
        type=int,
        help="when not zero, will truncate the observation to this length before feeding to the model",
        default=1920,
    )
    parser.add_argument(
        "--model_endpoint",
        help="huggingface model endpoint",
        type=str,
        default="",
    )

    # logging related
    parser.add_argument("--result_dir", type=str, default="")

    # manual related
    parser.add_argument("--note", type=str, default="")
    parser.add_argument("--no_manual", action="store_true")
    parser.add_argument("--skip_step", type=int, default=0) # todo: add skip_step = -1 for testing removing every single step thoroughly
    parser.add_argument("--narrative", action="store_true")
    parser.add_argument("--ui_change", action="store_true")
    parser.add_argument("--imperfect_aware", action="store_true")
    parser.add_argument("--abstraction", type=str, default='None', choices=['None', 
                                                                            'page_level',
                                                                            'task_specific'])
    parser.add_argument("--hint", type=str, default='None')
    parser.add_argument("--domain", type=str, default='reddit', choices=['reddit',
                                                                        'shopping', 
                                                                        'shopping_admin',
                                                                        'gitlab'])
    parser.add_argument("--swap", type=int, default=0)
    parser.add_argument("--typo", type=int, default=0)
    parser.add_argument("--delayed_obs", action="store_true")

    args = parser.parse_args()

    # check the whether the action space is compatible with the observation space
    if (
        args.action_set_tag == "id_accessibility_tree"
        and args.observation_type != "accessibility_tree"
    ):
        raise ValueError(
            f"Action type {args.action_set_tag} is incompatible with the observation type {args.observation_type}"
        )

    return args


def early_stop(
    trajectory: Trajectory, max_steps: int, thresholds: dict[str, int]
) -> tuple[bool, str]:
    """Check whether need to early stop"""

    # reach the max step
    num_steps = (len(trajectory) - 1) / 2
    if num_steps >= max_steps:
        return True, f"Reach max steps {max_steps}"

    last_k_actions: list[Action]
    action_seq: list[Action]

    # Case: parsing failure for k times
    k = thresholds["parsing_failure"]
    last_k_actions = trajectory[1::2][-k:]  # type: ignore[assignment]
    if len(last_k_actions) >= k:
        if all(
            [
                action["action_type"] == ActionTypes.NONE
                for action in last_k_actions
            ]
        ):
            return True, f"Failed to parse actions for {k} times"

    # Case: same action for k times
    k = thresholds["repeating_action"]
    last_k_actions = trajectory[1::2][-k:]  # type: ignore[assignment]
    action_seq = trajectory[1::2]  # type: ignore[assignment]

    if len(action_seq) == 0:
        return False, ""

    last_action: Action = action_seq[-1]

    if last_action["action_type"] != ActionTypes.TYPE:
        if len(last_k_actions) >= k:
            if all(
                [
                    is_equivalent(action, last_action)
                    for action in last_k_actions
                ]
            ) and str(last_k_actions[-1]['action_type']) != 'ACTION_TYPES.SCROLL': #you can scroll up and down for multiple times
                return True, f"Same action for {k} times"

    else:
        # check the action sequence
        if (
            sum([is_equivalent(action, last_action) for action in action_seq])
            >= k
        ):
            return True, f"Same typing action for {k} times"

    return False, ""


def get_manual( config_file,
                task_id,
                intent,
                agent,
                colored_logger,
                args,
                ):

    # Load the JSON file
    with open('config_files/test.json', 'r') as file:
        data = json.load(file)
    task_str = ''.join(data[task_id]['sites'])
    try:
        demo_file_path1 = f"./extracted_data/{task_str}/{task_id}/human.pkl"
        demo_file_path2 = f"/mnt/brain6/scratch/violetfy/webarena/extracted_data/{task_str}/{task_id}/human.pkl"  # Modify this path accordingly
        demo_file_path3 = f"/mnt/brain6/sayyappr/extracted_data/{task_str}/{task_id}/human.pkl"
        demo_file_path4 = f"/mnt/brain6/tanghj/extracted_data//{task_str}/{task_id}/human.pkl"
        

        if os.path.exists(demo_file_path1):
            demo_file = open(demo_file_path1, 'rb')
        elif os.path.exists(demo_file_path2):
            demo_file = open(demo_file_path2, 'rb')
        elif os.path.exists(demo_file_path3):
            demo_file = open(demo_file_path3, 'rb')
        elif os.path.exists(demo_file_path4):
            demo_file = open(demo_file_path4, 'rb')
        else:
            raise FileNotFoundError("Both demonstration files are missing.")

        demo = pickle.load(demo_file)
        demo_file.close()
    except Exception as e:
        return 'Error', None


    # keys: 'trajectory', 'metadata', 'intent', 'instruction_path', 'raw_actions', 'result'
    manual_info = ''

    manual, imperfect_info = format_manual( config_file, 
                                            demo,
                                            task_id,
                                            args,
                                            skip_step=1,
                                            narrative=False,
                                            abstraction=args.abstraction,
                                            ui_change=args.ui_change,
                                            logger=colored_logger)
    manual, imperfect_info = format_manual( config_file, 
                                            demo,
                                            task_id,
                                            args,
                                            skip_step=args.skip_step,
                                            narrative=args.narrative,
                                            abstraction=args.abstraction,
                                            ui_change=False,
                                            logger=colored_logger)
    
    manual_info += manual
    return manual, manual_info



def run_one_task(env,
                 agent,
                 config_file,
                 max_steps,
                 early_stop_thresholds,
                 colored_logger,
                 args):
    # try:
    
    
    # get intent
    with open(config_file) as f:
        _c = json.load(f)
        intent = _c["intent"]
        task_id = _c["task_id"]
        # automatically login
        if _c["storage_state"]:
            cookie_file_name = os.path.basename(_c["storage_state"])
            comb = get_site_comb_from_filepath(cookie_file_name)
            temp_dir = tempfile.mkdtemp()
            # subprocess to renew the cookie
            subprocess.run(
                [
                    "python",
                    "browser_env/auto_login.py",
                    "--auth_folder",
                    temp_dir,
                    "--site_list",
                    *comb,
                ]
            )
            _c["storage_state"] = f"{temp_dir}/{cookie_file_name}"
            assert os.path.exists(_c["storage_state"])
            # update the config file
            config_file = f"{temp_dir}/{os.path.basename(config_file)}"
            with open(config_file, "w") as f:
                json.dump(_c, f)
                
    if os.path.exists(f"{args.result_dir}/render_{task_id}.html"):
        colored_logger.log(f"Result directory '{args.result_dir}' already exists. Skipping...")
        return task_id, 'no_demo_skipped'
                
    # render_helper = RenderHelper(
    #     config_file, args.result_dir, args.action_set_tag
    # )

    logger.info(f"[Config file]: {config_file}")
    logger.info(f"[Intent]: {intent}")

    agent.reset(config_file)
    if args.no_manual:
        manuals, manual_info = 'None', 'None'
    else:
        manuals, manual_info = get_manual(config_file,
                                            task_id,
                                            intent,
                                            agent,
                                            colored_logger,
                                            args,)
   
    

def test(
    args: argparse.Namespace,
    agent: Agent | PromptAgent | TeacherForcingAgent,
) -> None:
    scores = []
    max_steps = args.max_steps

    early_stop_thresholds = {
        "parsing_failure": args.parsing_failure_th,
        "repeating_action": args.repeating_action_failure_th,
    }

    # colored_logger = ColoredLogger(args)
    # agent.prompt_constructor.colored_logger = colored_logger

    env = ScriptBrowserEnv(
        headless=not args.render,
        slow_mo=args.slow_mo,
        observation_type=args.observation_type,
        current_viewport_only=args.current_viewport_only,
        viewport_size={
            "width": args.viewport_width,
            "height": args.viewport_height,
        },
        save_trace_enabled=args.save_trace_enabled,
        sleep_after_execution=args.sleep_after_execution,
    )


    task_range = all_task_range[args.domain]['quick']
    # task_range = [x for x in task_range if x > 721]

    results, task_i = {}, 0

    # for config_file in config_file_list:
    while task_i < len(task_range):
        i = task_range[task_i]
        config_file = f"config_files/{i}.json"
        run_one_task(env,
                            agent,
                            config_file,
                            max_steps,
                            early_stop_thresholds,
                            None,
                            args)
       
        task_i += 1
       
    env.close()


def prepare(args: argparse.Namespace) -> None:
    # convert prompt python files to json
    from agent.prompts import to_json

    to_json.run()

    # prepare result dir
    result_dir = args.result_dir
    if not result_dir:
        result_dir = (
            f"cache/results_{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        )
    # if not Path(result_dir).exists():
    #     Path(result_dir).mkdir(parents=True, exist_ok=True)
    #     args.result_dir = result_dir
    #     logger.info(f"Create result dir: {result_dir}")

    # if not (Path(result_dir) / "traces").exists():
    #     (Path(result_dir) / "traces").mkdir(parents=True)

    # log the log file
    # with open(os.path.join(result_dir, "log_files.txt"), "a+") as f:
    #     f.write(f"{LOG_FILE_NAME}\n")


def get_unfinished(config_files: list[str], result_dir: str) -> list[str]:
    result_files = glob.glob(f"{result_dir}/*.html")
    task_ids = [
        os.path.basename(f).split(".")[0].split("_")[1] for f in result_files
    ]
    unfinished_configs = []
    for config_file in config_files:
        task_id = os.path.basename(config_file).split(".")[0]
        if task_id not in task_ids:
            unfinished_configs.append(config_file)
    return unfinished_configs


# def dump_config(args: argparse.Namespace) -> None:
#     config_file = Path(args.result_dir) / "config.json"
#     if not config_file.exists():
#         with open(config_file, "w") as f:
#             json.dump(vars(args), f, indent=4)
#             logger.info(f"Dump config to {config_file}")


if __name__ == "__main__":
    #set random seed for functions like skip_step for now
    random.seed(1)
    np.random.seed(1)
    
    args = config()
    args.sleep_after_execution = 2.0
    args.log_name = f"log"
    
    if args.provider == 'deepseek':
        prompt = 'p_manuals_deepseek'
    else:
        prompt = 'p_manuals'

    if args.domain.startswith('shopping_admin'):
        prompt = 'p_shopping_admin'
    else:
        prompt = prompt + '_aware' if args.imperfect_aware else prompt
        
    args.instruction_path = f'agent/prompts/jsons/{prompt}.json'
    manual_str = 'No_Manual' if args.no_manual else 'Manual'
    args.result_dir = args.result_dir + f'/{manual_str}::{args.model}::{prompt}/{args.domain}_{args.note}/Skip_{args.skip_step}::Narrative_{args.narrative}::Abs_{args.abstraction}::Swap_{args.swap}::Type_{args.typo}::{args.imperfect_aware}::UI_{args.ui_change}::Delayed_{args.delayed_obs}::Hint_{args.hint}'
    prepare(args)

    args.render = False
    args.render_screenshot = True
    args.save_trace_enabled = True

    args.current_viewport_only = True
    # dump_config(args)

    agent = construct_agent(args)
    test(args, agent)
    print(f'Experiment logs saved to {args.result_dir}')



# python agent/prompts/to_json.py
# python manual.py --model gpt-4o --result_dir exp_logs --skip_step 1
# python manual.py --model deepseek-r1:14b --result_dir exp_logs --note debug --provider deepseek
# python manual.py --model deepseek-r1:70b --result_dir exp_logs --provider deepseek --abstraction task_specific
# python manual.py --model deepseek-r1:70b --result_dir exp_logs --no_manual --provider deepseek --note first15

# python manual.py --model gpt-4o --result_dir exp_logs --skip_step 1 --imperfect_aware --hint specific


# docker exec shopping /var/www/magento2/bin/magento setup:store-config:set --base-url="http://141.212.113.68:7770" # no trailing slash
# docker exec shopping mysql -u magentouser -pMyPassword magentodb -e  'UPDATE core_config_data SET value="http://141.212.113.68:7770/" WHERE path = "web/secure/base_url";'
#

# python manual.py --model gpt-4o --result_dir exp_logs --note 


# python manual.py --model gpt-4o --result_dir ./exp_logs --note 27-408