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
from evaluation_harness import evaluator_router
from exp_utils.colored_logger import ColoredLogger
from exp_utils.gen_manuals import format_manual, extract_and_format_mapping
from exp_utils.task_range import all_task_range
from pdb import set_trace as st


SERVER_HOST=os.environ.get("SERVER_HOST", "localhost")
SERVER_PORT=os.environ.get("SERVER_PORT", "8080")
DATA_FOLDER=os.environ.get("DATA_FOLDER", "./extracted_data")


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
        demo_file_path = f"./extracted_data/{task_str}/{task_id}/human.pkl"

        if os.path.exists(demo_file_path):
            demo_file = open(demo_file_path, 'rb')
        else:
            raise FileNotFoundError("Both demonstration files are missing.")

        demo = pickle.load(demo_file)
        demo_file.close()
    except Exception as e:
        colored_logger.log(f"\033[32mFailed to load demonstration for this task \033[33m")
        return 'Error', None


    # keys: 'trajectory', 'metadata', 'intent', 'instruction_path', 'raw_actions', 'result'
    manual_info = ''
    manual, imperfect_info = extract_and_format_mapping(DATA_FOLDER, task_str, task_id)
    # manual, imperfect_info = format_manual( config_file, 
    #                                         demo,
    #                                         args,
    #                                         skip_step=args.skip_step,
    #                                         narrative=args.narrative,
    #                                         abstraction=args.abstraction,
    #                                         ui_change=args.ui_change,
    #                                         logger=colored_logger)
    colored_logger.log(f"\033[32mLoaded Manual for task \033[33m{intent}\033[0m:\n{manual}\033[0m")
    manual_info += manual
    colored_logger.log(f"\nImperfect Info: {imperfect_info}")
    manual_info += f"\nImperfect Info: {imperfect_info}" # full information, manual + imperfect_info
    # st()
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
                
    render_helper = RenderHelper(
        config_file, args.result_dir, args.action_set_tag
    )

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
    if manuals == 'Error':
        return task_id, 'no_demo_skipped'
    
    trajectory: Trajectory = []
    obs, info = env.reset(options={"config_file": config_file})
    while 'Whoops, something went wrong on our end.' in obs['text']:
        print('refreshing')
        obs, _, terminated, _, info = env.step(create_id_based_action('goto [http://gitlab.com]'))


    state_info: StateInfo = {"observation": obs, "info": info}
    trajectory.append(state_info)

    meta_data = {"action_history": ["None"]}
    meta_data['manuals'] = manuals
    meta_data['manual_info'] = manual_info

    step_i = 0
    last_obs = []
    last_ob = obs
    
    triggered = 0
    last_obs = [obs for _ in range(random.randint(2, 3))]
    while True:
        if manuals != "None":
            max_steps = len(manuals.split('\n')) + 12
        else:
            max_steps = args.max_steps
            
        early_stop_flag, stop_info = early_stop(
            trajectory, max_steps, early_stop_thresholds
        )

        colored_logger.log(f"\033[34mObs {step_i}\033[0m: \n{obs['text']}")
        colored_logger.log(f"\033[34mURL {step_i}\033[0m: \n{agent.prompt_constructor.map_url_to_real(info['page'].url)}")
        colored_logger.log(meta_data['manual_info'])

        if early_stop_flag:
            action = create_stop_action(f"Early stop: {stop_info}")
        else:
            try:
                action = agent.next_action(
                    trajectory, intent, meta_data=meta_data
                )
            except ValueError as e:
                # get the error message
                action = create_stop_action(f"ERROR: {str(e)}")
                colored_logger.log(f"\033[32mCreating an error stop action for \033[0m \n{str(e)}")

        colored_logger.log(f"\033[35mAction {step_i}\033[0m: \n{action['raw_prediction']}")
        colored_logger.log(f"\033[36mIntent\033[0m: {intent}")
        trajectory.append(action)
        step_i += 1

        action_str = get_action_description(
            action,
            state_info["info"]["observation_metadata"],
            action_set_tag=args.action_set_tag,
            prompt_constructor=agent.prompt_constructor
            if isinstance(agent, PromptAgent)
            else None,
        )
        render_helper.render(
            action, state_info, meta_data, args.render_screenshot
        )
        meta_data["action_history"].append(action_str)

        if action["action_type"] == ActionTypes.STOP:
            break

        last_url = agent.prompt_constructor.map_url_to_real(info['page'].url)
        
        obs, _, terminated, _, info = env.step(action)
        obs_rec = obs
        if args.delayed_obs:
            if last_obs:
                colored_logger.log(f"\033[36mObs delayed\033[0m")
                obs = last_obs.pop()
            elif random.random() < 0.3 and triggered < 2:
                last_obs = [last_ob for _ in range(random.randint(2, 5))]
                triggered += 1

        last_ob = obs_rec #this comes from the environment

        while 'Whoops, something went wrong on our end.' in obs['text']:
            print(f'refreshing, navigating to {last_url}')
            obs, _, terminated, _, info = env.step(create_id_based_action(f'goto [{last_url}]'))
        
        if 'You cannot post more.' in obs['text']:
            # let's try the task again
            render_helper.close()
            return task_id, 'post_issue_retry'
        state_info = {"observation": obs, "info": info}
        trajectory.append(state_info)

        if terminated:
            # add a action place holder
            trajectory.append(create_stop_action(""))
            break

    if args.delayed_obs:
        colored_logger.log(f"\033[36mObs delay\033[0m: {triggered}")
    evaluator = evaluator_router(config_file)
    score = evaluator(
        trajectory=trajectory,
        config_file=config_file,
        page=env.page,
        client=env.get_page_client(env.page),
    )
    if args.domain == 'shopping_admin':
        post_process(env)
    render_helper.close()
    return task_id, score

def post_process(env):
    for link in [f'${SERVER_HOST}:${SERVER_PORT}/admin/reports/report_review/product/filter',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/reports/report_review/customer/',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/reports/report_review/product/',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/search/term/report/',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/reports/report_product/lowstock/',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/reports/report_product/downloads/',
                 f'${SERVER_HOST}:${SERVER_PORT}/admin/paypal/paypal_reports/']:
        
        obs, _, terminated, _, info = env.step(create_id_based_action(f'goto [{link}]'))
        id = obs['text'].split("] button 'Reset Filter'")[0].split('[')[-1]
        env.step(create_id_based_action(f'click [{id}]'))
    
    

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

    colored_logger = ColoredLogger(args)
    agent.prompt_constructor.colored_logger = colored_logger

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
        task_id, score = run_one_task(env,
                             agent,
                             config_file,
                             max_steps,
                             early_stop_thresholds,
                             colored_logger,
                             args)
        if score == 'post_issue_retry':
            colored_logger.log('you should delete extra reddit posts to continue')
            st()
        else:
            if score == 'no_demo_skipped':
                logger.info(f"[Result] (No demo for the task, skipped.) {config_file}")
            else:
                scores.append(score)
                if score == 1:
                    logger.info(f"[Result] (PASS) {config_file}")
                else:
                    logger.info(f"[Result] (FAIL) {config_file}")

                if args.save_trace_enabled:
                    env.save_trace(
                        Path(args.result_dir) / "traces" / f"{task_id}.zip"
                    )
            task_i += 1
            results[i] = score

            for key in results:
                colored_logger.log(key, results[key])
            colored_logger.log('results:', np.mean([s for s in list(results.values()) if type(s) != str]))

    env.close()
    logger.info(f"Average score: {np.mean(scores)}")
    colored_logger.log(f"Average score: {np.mean(scores)}")


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
    if not Path(result_dir).exists():
        Path(result_dir).mkdir(parents=True, exist_ok=True)
        args.result_dir = result_dir
        logger.info(f"Create result dir: {result_dir}")

    if not (Path(result_dir) / "traces").exists():
        (Path(result_dir) / "traces").mkdir(parents=True)

    # log the log file
    with open(os.path.join(result_dir, "log_files.txt"), "a+") as f:
        f.write(f"{LOG_FILE_NAME}\n")


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


def dump_config(args: argparse.Namespace) -> None:
    config_file = Path(args.result_dir) / "config.json"
    if not config_file.exists():
        with open(config_file, "w") as f:
            json.dump(vars(args), f, indent=4)
            logger.info(f"Dump config to {config_file}")


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
    dump_config(args)

    agent = construct_agent(args)
    test(args, agent)
    print(f'Experiment logs saved to {args.result_dir}')


