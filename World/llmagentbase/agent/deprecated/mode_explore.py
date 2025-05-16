import re
import copy
import numpy as np
from common.llms import llm
from llmagentbase.agent.navigator import Navigator
from llmagentbase.prompts.navigation_planner import *
from pdb import set_trace as st

def extract_plans(text):
    summary_match = re.search(r'^(.*?)(?:\n\*?\*?Plan\s+\d+:)', text, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""

    plan_pattern = r'(?:\*?\*?Plan\s+\d+:.*?\n)(.*?)(?=(?:\n\*?\*?Plan\s+\d+:)|\Z)'
    raw_plans = re.findall(plan_pattern, text, re.DOTALL)

    cleaned_plans = []
    for block in raw_plans:
        purpose_match = re.search(r'Purpose:.*?(?=\n[A-Z][a-z]+:|\Z)', block, re.DOTALL)
        action_match = re.search(r'Potential Action Sequence:.*?(?=\n[A-Z][a-z]+:|\Z)', block, re.DOTALL)

        purpose = purpose_match.group(0).strip() if purpose_match else ""
        action = action_match.group(0).strip() if action_match else ""

        if purpose:
            cleaned_plans.append(purpose)

    return summary, cleaned_plans


def extract_answer(output: str) -> int:
    match = re.search(r'Answer:\s*(\d+)', output.strip(), re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    match = re.search(r'(\d+)\s*$', output.strip())
    if match:
        return int(match.group(1))
    

class Explorer(Navigator):
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    manual_type,
                    mode_type,
                    exploration_model,
                    ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature,
                        manual_type)
        self.manual_type = manual_type
        self.identifider_accuracies = []
        self.exploration_model = exploration_model
        self.mode_type = mode_type
        self.mode_recs = []


    def construct_prompt(self,
                         traj,
                         reasoning='',
                        ):
        if self.manual_type == 0:
            prompt = f"{self.instruction}\n{mode_action}\nNow it's your turn:\n"
        else:
            prompt = f"{self.instruction}\n{mode_action}\nNow it's your turn:\nStep-by-Step Guide to Complete the Task:\n{self.manual}\n\nTry your best to navigate to the destination:\n"
        if reasoning:
            prompt += f"{traj}\nReasoning: it seems that the guide does not fully match your status now, here are some reasonings about what to do potentially for the next step: {reasoning}\n\nAction: "
        else:
            prompt += f"{traj}\nAction: "
        # print(f"\033[34mPrompt: \033[0m{prompt}")
        # st()
        return prompt
    
    def redo_actions(self):
        obs, reward, done, info = self.env.rewind()
        for action in self.action_seq:
            obs, reward, done, info = self.env.step(action) 
        return

    def follow_plan(self,
                    plan,
                    initial_obs):
        # first we need to simulate until the current state. 
        self.redo_actions()
        traj = f"Observation: {initial_obs}\n" # we ignore the epi history for exploration? 
        actions = []
        for _ in range(10): # we can explore for at most 10 steps
            prompt = follow_subgoal.format(selected_plan=plan,
                                           traj=traj)
            action = self.get_action(prompt, max_tokens=256, stop=['\nObservation', 'Action: '])
            actions.append(action)
            if action == 'stop':
                curr_step = f'\nAction: {action}'
                traj += curr_step
                break
            obs, reward, done, info = self.step(action)
            curr_step = f'\nAction: {action}\nObservation: {obs}\n'
            traj += curr_step
            self.logger.log(f"\033[35mExploration step: \033[0m{curr_step}")
        # return self.epi_no_thinking(traj)
        return traj, actions


    def explore_surrondings(self, 
                            traj,
                            obs):
        # this is only with reasoning model actually
        full_prompt = explore_subgoal.format(guide=self.manual,
                                            traj=traj)
        answer = llm(full_prompt,
                     model_name=self.exploration_model,
                     temperature=self.temperature,
                     max_tokens=1024,
                     )
        _, plans = extract_plans(answer)
        self.logger.colored_log("Proposed Plans:", answer, color="yellow", bold=True)
        gathered_info = ''
        all_explorations = []
        for idx, plan in enumerate(plans):
            self.logger.log(f"\033[36mStart to explore with plan: \033[0m{idx+1}\n{plan}")
            info, actions = self.follow_plan(plan,
                                            obs)
            all_explorations.append(actions)
            info = self.epi_no_thinking(info)
            gathered_info += f"Exploration with plan {idx+1}: \n{plan}\nHere are the steps: \n{info}\n"

        self.redo_actions() # go back to the initial
        full_prompt = best_selection.format(guide=self.manual,
                                            traj=traj,
                                            info=gathered_info,
                                            last_obs=obs)
        # answer = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', 'Action: '])
        answer = llm(full_prompt,
                    #  model_name='gpt-4o',
                    #  model_name='o3-mini',
                    #  model_name='gpt-4o-mini',
                     model_name=self.exploration_model,
                     temperature=self.temperature,
                     max_tokens=512,
                     stop=['\nObservation', 'Action: '],
                     )
        self.logger.log(f"\033[31mSelection Reasoning: \033[0m{answer}")
        idx = extract_answer(answer)
        # print(idx)
        # st()
        if idx == 0 or idx == 1:
            return 'switch_mode'
        if idx > len(all_explorations):
            idx = 1
        actions = [xx for xx in all_explorations[idx-1] if not xx.startswith('think')]
        seq = ', '.join(actions)
        action = f"think[I was following the guide, however, it seems that my current observation does not match what's described in the guide. Therefore, I sent out multiple agents to explore around. after exploration, the best sequence of future actions that I think will guide me back to the correct path is {seq}.]"
        return action
        
    def run(self,
            task_name,
            trial,
            args):
        
        observation, reward, done, info, epi_history, step_count = self.reset_env()
        full_history = ''
        self.action_seq = []
        action = ''
        actions = []
        mode_reasoning = ''

        self.logger.log(f"\033[34mObservation {step_count}: \033[0m{observation}")
        self.logger.log()

        for i in range(self.env.get_horizon()): # we only record the actions themselves, not the exploration steps. 
            
            if i:
                curr_step = f'\nAction: {action}\nObservation: {observation}\n'
                step_count += 1
            else:
                curr_step = f'Observation: {observation}\n'

            epi_history += curr_step
            full_history += curr_step

            if done:
                break

            if not action.startswith('think'):
                gt_mode = self.env.get_gt_mode()
                if self.mode_type == 'gt':
                    mode = gt_mode if gt_mode == 'Follow' else 'Explore'
                elif self.mode_type == 'pred':
                    identifider_prompt = p_mode_switch.format(manual=self.manual,
                                                              traj=full_history)
                    # print(identifider_prompt)
                    # st()
                    mode_reasoning = self.get_action(identifider_prompt, max_tokens=256, stop=['\nObservation', 'Action: ', '\nMode: '])
                    mode_reasoning = f"\nMode: {mode_reasoning}\n"
                    self.logger.log(f"\033[35mMode {step_count}: \033[0m{mode_reasoning}")
                    match = re.search(r'my current mode should be:\s*(Follow|Explore|follow|explore)', mode_reasoning, re.IGNORECASE)
                    if match:
                        mode = match.group(1).capitalize()
                    else:
                        mode = 'Follow'
                    if mode not in ['Explore', 'Follow']:
                        mode = 'Follow'
                    self.mode_recs.append((gt_mode, mode))
                
                self.logger.log(f"\033[32mGT Mode: \033[0m{gt_mode}, \033[33mApplied Mode: \033[0m{mode}")
            else:
                mode_reasoning = ''
    
            if action.startswith('think') or mode == 'Follow':
                full_prompt = self.construct_prompt(traj = epi_history)
                action = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', 'Action: '])
            elif mode == 'Explore':
                action = self.explore_surrondings(epi_history, observation)
                if action == 'switch_mode':
                    full_prompt = self.construct_prompt(traj = epi_history)
                    action = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', 'Action: '])
                    mode_reasoning = 'After exploration, I think the best action is still to follow the guide. Therefore, my current mode should be: Follow.'
                    mode_reasoning = f"\nMode: {mode_reasoning}\n"
            self.action_seq.append(action)

            full_history += mode_reasoning

            # action = input("Enter your action: ")
            self.log_frame(action, i)

            observation, reward, done, info = self.step(action, reward, done, info)

            if 'warning' in info and observation != 'OK.':
                observation = f"{observation}\n{info['warning']}"

            self.logger.log(f"\033[34mAction {step_count}: \033[0m{action}")
            self.logger.log(f"\033[34mObservation {step_count+1}: \033[0m{observation}")
            self.logger.log()
            
        epi_history = '\nObservation:'.join(epi_history.split('\nObservation:')[:-1])
        msg = ''
        if not done:
            msg = f'\nObservation: Maximum Step Exceeded, task failed. '
        if reward == 1:
            msg = f'\nObservation: Task completed successfully.'
        epi_history += msg
        return reward, epi_history, step_count
