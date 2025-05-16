import re
import numpy as np
from common.llms import llm
from llmagentbase.agent.navigator import Navigator
from llmagentbase.prompts.navigation_planner import *
from llmagentbase.prompts.navigation_reason import reason_prompt
from pdb import set_trace as st


class Planner(Navigator):
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
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\n"
        else:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nStep-by-Step Guide to Complete the Task:\n{self.manual}\n\nTry your best to navigate to the destination:\n"
        if reasoning:
            prompt += f"{traj}\nReasoning: it seems that the guide does not fully match your status now, here are some reasonings about what to do potentially for the next step: {reasoning}\n\nAction: "
        else:
            prompt += f"{traj}\nAction: "
        # print(f"\033[34mPrompt: \033[0m{prompt}")
        # st()
        return prompt
    
    def identifider_prompt(self, 
                           traj):
        assert self.manual_type != 0, 'You must have a manual to work with.'
        prompt = f"{p_mode_switch}\nNow it's your turn:\nStep-by-Step Guide to Complete the Task:\n{self.manual}\nTrajectory:\n{traj}\nMode: "
        # print(f"\033[34mPrompt: \033[0m{prompt}")
        # st()
        return prompt

    def explore_surrondings(self, 
                            action_history,
                            traj):
        # this is only with reasoning model actually
        full_prompt = reason_prompt.format(guide=self.manual,
                                            traj=traj)
        reasoning = llm(full_prompt,
                        model_name=self.exploration_model,
                        temperature=self.temperature)
        
        self.logger.log(f"\033[33mReasoning: \033[0m{reasoning}")
        # for deepseek let's only get the thinking steps becuase somehow it cut off sometmes
        match = re.search(r'<think>\s*(.*?)\s*</think>', reasoning, re.DOTALL)
        if match:
            reasoning = match.group(1)

        full_prompt = self.construct_prompt(traj = traj,
                                            reasoning=reasoning)
        # st()
        action = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', 'Action: ']).replace('\n', ' ').lstrip().strip()
        return action
        
    def run(self,
            task_name,
            trial,
            args):
        
        observation, reward, done, info, epi_history, step_count = self.reset_env()
        full_history = ''
        action_seq = []
        action = ''
        self.logger.log(f"\033[34mObservation {step_count}: \033[0m{observation}")
        self.logger.log()

        for i in range(self.env.get_horizon()):

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
                    identifider_prompt = self.identifider_prompt(traj = full_history)
                    mode_reasoning = self.get_action(identifider_prompt, max_tokens=256, stop=['\nObservation', 'Action: ', '\nMode: '])
                    
                    self.logger.log(f"\033[35mMode {step_count}: \033[0m{mode_reasoning}")
                    match = re.search(r'my current mode should be:\s*(Follow|Explore|follow|explore)', mode_reasoning, re.IGNORECASE)
                    full_history += f"\nMode: {mode_reasoning}\n"
                    if match:
                        mode = match.group(1).capitalize()
                    else:
                        mode = 'Follow'
                    if mode not in ['Explore', 'Follow']:
                        mode = 'Follow'
                    self.mode_recs.append((gt_mode, mode))
                self.logger.log(f"\033[32mGT Mode: \033[0m{gt_mode}, \033[33mPredicted Mode: \033[0m{mode}")
            
            if action.startswith('think') or mode == 'Follow':
                full_prompt = self.construct_prompt(traj = epi_history)
                action = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', 'Action: '])
            elif mode == 'Explore':
                action = self.explore_surrondings(action_seq,
                                                  epi_history)
            action_seq.append(action)
                
            # action = input("Enter your action: ")
            self.log_frame(action, i)
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()) or ('task completed successfully' in action.lower()):
                break

            if action.startswith('think'):
                observation = 'OK.'
            else:
                try:
                    observation, reward, done, info = self.env.step(action)
                except AssertionError as e:
                    self.logger.log(f"[red][Error][/]: {e}", option='console')
                    observation = f'Invalid action! '

            if 'warning' in info and observation != 'OK.':
                observation = f"{observation}\n{info['warning']}"

            self.logger.log(f"\033[34mAction {step_count}: \033[0m{action}")
            self.logger.log(f"\033[34mObservation {step_count+1}: \033[0m{observation}")
            self.logger.log()
            
        epi_history = '\nObservation:'.join(epi_history.split('\nObservation:')[:-1])
        if not done:
            epi_history += f'\nObservation: Maximum Step Exceeded, task failed. '
        if reward == 1:
            epi_history += f'\nObservation: Task completed successfully.'
        # print(epi_history)

        return reward, epi_history, step_count
