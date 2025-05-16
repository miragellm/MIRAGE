import numpy as np
from .base import Agent
from pdb import set_trace as st

class Adventurer(Agent):
    def __init__(self, 
                env,
                instruction,
                in_context,
                logger,
                model_name,
                temperature,
                manual_type=0
                ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature)
        self.manual_type = manual_type
        self.game_history = []
        self.action_stats = {}
        self.available_actions = []
        self.mode_recs = []

    def construct_prompt(self, traj):
        if self.manual_type is None:
            if self.reflection:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nSomething useful:\n{self.manual}\n\n{self.reflection}\nTry your best to complete the game:\n"
            else:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nSomething useful:\n{self.manual}\n\nTry your best to complete the game:\n"
        else:
            if self.reflection:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nStrategy Guide for Roguelike Game:\n{self.manual}\n\n{self.reflection}\nTry your best to complete the game:\n"
            else:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nStrategy Guide for Roguelike Game:\n{self.manual}\n\nTry your best to complete the game:\n"
        prompt += f"{traj}\nAction: "
        # if self.reflection:
        # print(prompt)
        # st()
        return prompt
    
    def reset_env(self):
        reward, done, info = 0, False, {}
        epi_history = ''
        step_count = 0

        if self.trial == 0:
            observation = self.env.reset()
        else:
            self.env.back_to_start()
        observation, self.manual = self.env.get_manual(self.manual_type)
        self.logger.colored_log("Loaded Strategy Guide:", self.manual, color="yellow")
        self.logger.colored_log("Max Steps:", self.env.get_horizon(), color="green")
        return observation, reward, done, info, epi_history, step_count
    
    def process_game_info(self, info):
        """Process game state information to track available actions"""
        if 'game_state' in info and 'available_actions' in info['game_state']:
            self.available_actions = info['game_state']['available_actions']
            return ", ".join(self.available_actions)
        return ""
   
    
    def run(self, 
            task_name, 
            trial, 
            reflection, 
            args):
        # Reset game environment
        self.trial = trial
        self.reflection = reflection
        observation, reward, done, info, epi_history, step_count = self.reset_env()
        self.logger.colored_log(f"Observation {step_count}:", observation, color="blue")
        self.logger.log()
        
        total_reward = 0
        self.game_history = []
        self.action_stats = {}
        action_lst = []
        
        consecutive_think = 0
        repeated_think = 0
        last_think = ''
        epi_history = []

        for i in range(self.env.get_horizon()):
            if i:
                curr_step = f'\nAction: {action}\nObservation: {observation}\n'
                step_count += 1
                
                # Track game progress
                self.game_history.append({
                    'action': action,
                    'observation': observation,
                    'reward': reward
                })
                total_reward += reward
            else:
                curr_step = f'Observation: {observation}\n'

            # epi_history += curr_step
            epi_history.append(curr_step)
            if done:
                break

            # Get available actions from the info dictionary
            available_actions_text = self.process_game_info(info)
            if i > 20:
                prefix = '...omitting previous steps...\n'
            else:
                prefix = ''

            if available_actions_text:
                full_prompt = self.construct_prompt(traj=prefix+''.join(epi_history[-20:]) + f"\nAvailable actions: {available_actions_text}\n")
            else:
                full_prompt = self.construct_prompt(traj=prefix+''.join(epi_history[-20:]))

            if self.model_name == 'human':
                if i < len(action_lst):
                    action = action_lst[i]
                else:
                    action = input("Enter your action: ")
            else:
                action = self.get_action(full_prompt, max_tokens=256, stop=["Observation:", "\nAction: "])
            # self.track_action(action)
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()):
                break

            if action.startswith('Action:'):
                action = action.split('Action:')[1]

            if action.startswith('think') or action.startswith('<think>'):
                observation = 'OK.'
                consecutive_think += 1
                if action == last_think:
                    repeated_think += 1
            else:
                consecutive_think = 0
                repeated_think = 0
                try:
                    observation, reward, done, info = self.env.step(action)
                except AssertionError as e:
                    self.logger.colored_log("Error:", e, color="red")
                    observation = f'Invalid action! '

            last_think = action
            if consecutive_think >= 5 or repeated_think >= 3:
                break

            if 'warning' in info and observation != 'OK.':
                observation = f"{observation}\n{info['warning']}"

            self.logger.colored_log(f"Action {step_count}:", action, color="blue")
            self.logger.colored_log(f"Observation {step_count+1}:", observation, color="blue")
            self.logger.log() 
            if "You have been defeated! Game over." in observation:
                done = True

        epi_history = ''.join(epi_history)
        epi_history = '\nObservation:'.join(epi_history.split('\nObservation:')[:-1])
        if not done:
            epi_history += f'\nObservation: Maximum Step Exceeded, game failed. '
        elif reward > 0:
            epi_history += f'\nObservation: Game completed successfully!'
        
        # Print analytics
        self.logger.colored_log("=== Game Statistics ===", color="green")
        self.logger.log(f"Total Reward: {total_reward}")
        self.logger.log(f"Total Steps: {step_count}")
        self.logger.log(f"Actions Used: {self.action_stats}")
        
        return reward, epi_history, step_count