import cv2
import pygame
import numpy as np
import textwrap
from llmagentbase.agent.base import Agent
from pdb import set_trace as st

class Chef(Agent):
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    manual_type
                    ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature)
        self.manual_type = manual_type
        self.mode_recs = []


    def construct_prompt(self,
                         traj
                        ):
        if self.manual_type is None:
            if self.reflection:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\n{self.reflection}\n"
            else:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\n"
        else:
            if self.reflection:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nRecide of the required dish(es):\n{self.manual}\n\n{self.reflection}\nTry your best to complete the required dish(es):\n"
            else:
                prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nRecide of the required dish(es):\n{self.manual}\n\nTry your best to complete the required dish(es):\n"

        prompt += f"{traj}\nAction: "
        # print(f"\033[34mPrompt: \033[0m{prompt}")
        # st()
        return prompt
    
    def reset_env(self):
        reward, done, info = 0, False, {}
        epi_history = ''
        step_count = 0

        if self.trial == 0:
            observation = self.env.reset()
        else:
            observation = self.env.back_to_start()
        self.manual, self.imperfect_info = self.env.get_manual(self.manual_type)
        self.env.simulate_env_variants()
        self.logger.log(f"\033[33mLoaded Manual: \033[0m{self.manual}")
        self.logger.log(f"\033[33mImperfect Info: \033[0m{self.imperfect_info}")
        self.logger.log(f"\033[32mHorizon: \033[0m{self.env.get_horizon()}")
        return observation, reward, done, info, epi_history, step_count
        
    def run(self,
            task_name,
            trial,
            reflection,
            args):
        # reset task
        self.reflection = reflection
        self.trial = trial
        observation, reward, done, info, epi_history, step_count = self.reset_env()
        self.logger.log(f"\033[34mObservation {step_count}: \033[0m{observation}")
        self.logger.log()

        action_lst = []

        consecutive_think = 0
        repeated_think = 0
        last_think = ''
        
        for i in range(self.env.get_horizon()):
            if i:
                curr_step = f'\nAction: {action}\nObservation: {observation}\n'
                step_count += 1
            else:
                curr_step = f'Observation: {observation}\n'

            epi_history += curr_step

            if done:
                break

            full_prompt = self.construct_prompt(traj = epi_history # traj = '' to disable history
                                                )
            
            if self.model_name == 'human':
                if i < len(action_lst):
                    action = action_lst[i]
                else:
                    action = input("Enter your action: ")
            else:
                action = self.get_action(full_prompt, 
                                         max_tokens=256, 
                                         stop=['Observation', '\nAction: '],
                                         reset_context=(i==0))
            self.log_frame(action, i)
            if action.startswith('Action:'):
                action = action.split('Action:')[1]
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()) or ('in a loop' in action.lower()):
                self.logger.log(action)
                break

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

            self.logger.log(f"\033[34mAction {step_count}: \033[0m{action}")
            self.logger.log(f"\033[34mObservation {step_count + 1}: \033[0m{observation}")
            self.logger.log()
            
        epi_history = '\nObservation:'.join(epi_history.split('\nObservation:')[:-1])
        if not done:
            epi_history += f'\nObservation: Maximum Step Exceeded, task failed. '
        if reward == 1:
            epi_history += f'\nObservation: Task completed successfully.'
        # print(epi_history)
        # st()

        return reward, epi_history, step_count

    def log_frame(self, action, step, add_to_history=True):
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = np.rot90(frame, k=-1)
        frame = np.fliplr(frame)
        action = f'Action {step+1}: {action}'
        frame = self.add_text_to_frame(frame, action)

        if add_to_history:
            self.logger.log_frame(frame)


    def add_text_to_frame(self, frame, action_text, font_scale=1, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
        # Get original frame dimensions
        height, width, channels = frame.shape
        extra_space_right = width  # Add the same width as the original frame for self.manual
        text_height = 150  # Fixed extra space below

        # Create a new blank image with extra space on the right and below
        new_frame = np.full((height + text_height, width + extra_space_right, channels), bg_color, dtype=np.uint8)

        # Copy the original frame into the new image
        new_frame[:height, :width] = frame

        # Handle action text
        font_scale_rec = font_scale
        if "think[" in action_text:
            font_scale = font_scale * 0.5  # Reduce font size
            wrapped_text = textwrap.fill(action_text, width=65)
        else:
            wrapped_text = action_text

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2

        # Add action text below the original frame
        for i, line in enumerate(wrapped_text.split('\n')):
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2  # Centered below the image
            text_y = height + int((i + 1) * 30 * font_scale)
            cv2.putText(new_frame, line, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

        # Add self.manual text in the right extra space
        if hasattr(self, "manual") and self.manual:
            manual_x_start = width + 10  # Start manual text slightly inside the right space
            manual_y_start = 30  # Start text near the top of the right space

            # Process each original line separately
            count = 0
            for i, original_line in enumerate(self.manual.splitlines()):  # Preserve existing new lines
                wrapped_lines = textwrap.wrap(original_line, width=70)  # Wrap only if a line is too long

                for j, line in enumerate(wrapped_lines):
                    text_size = cv2.getTextSize(line, font, font_scale_rec * 0.5, thickness)[0]
                    text_x = manual_x_start  # Aligned to the right section
                    text_y = manual_y_start + int(count * 30 * font_scale_rec)  # Adjust for wrapped lines

                    cv2.putText(new_frame, line, (text_x, text_y), font, font_scale_rec * 0.5, text_color, thickness, cv2.LINE_AA)
                    count += 1
        return new_frame