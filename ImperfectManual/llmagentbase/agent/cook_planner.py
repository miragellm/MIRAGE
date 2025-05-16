import cv2
import pygame
import numpy as np
import textwrap
from llmagentbase.agent.base import Agent
from llmagentbase.utils import plan_to_str
from pdb import set_trace as st

plan_prompt = """In this task, you are a chef in a restaurant. You will be asked to cook some dishes for the customers. Some needed ingredients are already stored at the restaurant, but some are not. Therfore, you need to gather all needed ingredients at farm, store, and harbor, and then go back to the restaurant to cook the dish(es) in kitchen, with the goal of generating actions to complete all required dishes.
At each time step, you will be provided with the following inputs:
1. The result of your latest action.

You can only issue the following actions in this environment, one at a time:
    goto <location> -> You can go to restaurant, farm, store, and harbor_<id>, where harbor id includes 1, 2, 3.
    harvest <crop>
    fish <seafood>
    buy <ingredient>
    put <ingredient> into <tool> -> <tool> includes cooking tools, cutting_board, and plate_<id>.
    chop -> Chop the ingredient you are holding.
    wait -> Use this when you have nothing more to do but some <tool> hasn't finish cooking.
    plate from <tool> into plate_<id> -> You can only plate into a plate, not including other cooking tools.
    serve plate_<id> -> Use this after you finish a dish in a plate.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.


You will receive the following inputs:
1.	A step-by-step guide that may contain useful instructions or suggestions.
2.	The current episode history, including all previous observations and actions.
3.	Your previously generated high-level planning steps.

Your task:
Based on the information above, do simple and brief reasoning and then generate the next high-level planning step that the agent should follow.
This step should:
- Be a real planning step, not a low-level action.
- Include brief descriptive context (e.g., intent, condition, or direction).
- Logically follow the previous steps, without repeating or summarizing them.
- Be achievable in 10 or fewer low-level actions.

Important: If you have a Step-by-Step Guide, you can refer to it to write your plan. However, you should be cautious not to blindly follow it. Instead, you should read the provided trajectory to see what you have done. The previous plan steps may be followed successfully or wrongly. (The agent did less or more necessary steps). You should adjust your next planning step accordingly. 

Here are some example planning steps: 
Go to farm to find some lettuce. 
Go to the store to get chicken, cumin, paprika.
Go to a harbor to get shrimps. 
Go to the restaurant to cook the dish.
Continue cooking: pan-fry the raw shrimp, raw chicken and put seasonings.
Wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.


Here is an example:
Step-by-Step Guide to Complete the Task: 
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.

Trajectory:
Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I will visit farm, store, harbor one by one to get these ingredients. First, I will go to the farm.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[Among all the crops in the farm, lettuce is an ingredient I need. I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. I still need shrimp, chicken, cumin, paprika. Next, I will go to the store.]
Observation: OK.

Past plans: 
1. Go to farm, harvest lettuce if you find lettuce there.  

Reasoning: Now I harvested some lettuce. I can continue going to store to check if I can find raw chicken, paprika, cumin, and shrimp there.
Next plan step: Go to store, if you see raw chicken, paprika, cumin, and shrimp in the store, buy them. 

Now it's your turn: 
Step-by-Step Guide to Complete the Task: 
{guide}

Trajectory:
{traj}

Past plans: 
{plans}

Reasoning: """


class CookPlanner(Agent):
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
                         traj,
                         plan
                        ):
        if self.manual:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn: \nA guide that contains important information:{self.manual}\nCurrent subgoal: {plan}\nTrajectory:\n"
        else:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn: \nCurrent subgoal: {plan}\nTrajectory:\n"
        prompt += f"{traj}\nAction: "
        # print(prompt)
        # st()
        return prompt
    
    def plan_prompt(self,
                    traj):
        prompt = plan_prompt.format(guide = self.manual,
                                    traj=traj,
                                    plans=plan_to_str(self.plans),
                                    )
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
            observation = self.env.back_to_start()
        self.manual, self.imperfect_info = self.env.get_manual(self.manual_type)
        if self.manual_type is None:
            self.manual = ''
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

        consecutive_think = 0
        repeated_think = 0
        last_think = ''
        self.plans = []
        subgoal_done = True

        consecutive_think = 0
        repeated_think = 0
        last_think = ''
        
        i = 0
        action = ''
        full_history = ''
        last_non_think = observation
        while i < self.env.get_horizon():
            i += 1
            if i > 1:
                curr_step = f'\nAction: {action}\nObservation: {observation}\n'
                step_count += 1
            else:
                curr_step = f'Observation: {observation}\n'

            if action != 'stop':
                epi_history += curr_step
                full_history += curr_step

            if done:
                break

            if subgoal_done:
                high_level_prompt = self.plan_prompt(full_history)
                plan = self.get_action(high_level_prompt, 
                                       max_tokens=256,
                                       stop=['\nObservation', '\nAction: '])
                self.logger.colored_log("Answer:", plan, color="magenta")
                if 'Next plan step:' in plan:
                    plan = plan.split('Next plan step:')[1]
                plan = plan.strip()
                self.logger.colored_log("Plan:", plan, color="magenta")
                self.plans.append(plan)
                subgoal_done = False
                if i > 1:
                    epi_history = f'Observation: {self.env.get_status()}\n'
                else:
                    epi_history = f'Observation: {last_non_think}\n'
                consecutive_think = 0
                subgoal_step = 0

            full_prompt = self.construct_prompt(traj = epi_history, # traj = '' to disable history
                                                plan = plan)
            
            action = self.get_action(full_prompt, max_tokens=256, stop=['Observation', '\nAction: '])

            if action.startswith('Action:'):
                action = action.split('Action:')[1]

            if action.startswith('stop'):
                self.logger.colored_log(f"Action {step_count}:", 'stop', color="blue")
                subgoal_done = True
                subgoal_step = 0
                continue

            subgoal_step += 1
            # self.log_frame(action, i)
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()) or ('in a loop' in action.lower()):
                self.logger.log(action)
                break

            if action.startswith('think') or action.startswith('<think>'):
                action = action.split(']')[0] + ']'
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

            if subgoal_step >= 12:
                action == '\nWarning: This subgoal exceeds the 10-step limit.'
                subgoal_done = True
                subgoal_step = 0

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