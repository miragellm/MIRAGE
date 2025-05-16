import cv2
import pygame
import numpy as np
import textwrap
from llmagentbase.agent.base import Agent
from llmagentbase.utils import plan_to_str
from pdb import set_trace as st

plan_prompt = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination.
At each time step, you will be provided with the following inputs:
1. A first-person observation of the 3x3 surrounding tiles, with all unspecified tiles being lands with scattered stones.
2. The direction you are currently facing.
Here are more detailed explanations of the observation you get:
1. You are positioned at the center tile of the 3x3 tiles.

You can issue the following low level actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.

You will receive the following inputs:
1.	A step-by-step guide that may contain useful instructions or suggestions.
2.	The current episode history, including all previous observations and actions.
3.	Your previously generated high-level planning steps.

Your task:
Based on the information above, do simple and brief reasoning and then generate the next high-level planning step that the agent should follow.
This step should:
•	Be a real planning step, not a low-level action.
•	Include brief descriptive context (e.g., intent, condition, or direction).
•	Logically follow the previous steps, without repeating or summarizing them.
•	Be achievable in 10 or fewer low-level actions.

Important: If you have a Step-by-Step Guide, you can refer to it to write your plan. However, you should be cautious not to blindly follow it. Instead, you should read the provided trajectory to see what you have done. The previous plan steps may be followed successfully or wrongly. (The agent did less or more necessary steps). You should adjust your next planning step accordingly. 

Here is an example:
Step-by-Step Guide to Complete the Task: 
None.

Trajectory:
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[I can't move forward because the tile ahead isn't a road. But since there's a road to my left, I can turn right and follow it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now that the tile in front of me is a road, I can move forward along it.]
Observation: OK.

Past plans: 
1.	Turn to a direction where you can move forward (the front tile is road).

Reasoning: Now my front tile is road. To better explore the surrondings, I can just move forward along this road until I cannot move forward more. 
Next plan step: walk forward until you cannot move forward any more.


Here is another example:
Step-by-Step Guide to Complete the Task: 
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 3 tiles (north), after that you will see a group of green pines on the back-right tile and a house on the front-right tile.
Step 3. Turn left to face west.
Step 4. Move forward 2 tiles (west) to approach the destination.

Trajectory:
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Past plans: 
1.	Turn left until you are facing north. 

Reasoning: I have successfully turned left and now I'm facing north. Therefore I can follow the next step in the guide, which asks me to move forward 3 tiles towards north and stop when I see group of green pines on the back-right tile and a house on the front-right tile.
Next plan step: Move forward three tiles towards north and you will see a group of green pines on the back-right tile and a house on the front-right tile.

Now it's your turn: 
Step-by-Step Guide to Complete the Task: 
{guide}

Trajectory:
{traj}

Past plans: 
{plans}

Reasoning: """


class NavigatePlanner(Agent):
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

        if self.manual_type is not None:
            self.logger.colored_log("Loaded Manual:", self.manual, color="yellow")
            self.logger.colored_log("Imperfect Info:", self.imperfect_info, color="yellow")
        else:
            self.manual = 'None'
        self.logger.colored_log("Horizon:", self.env.get_horizon(), color="green")
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
        self.logger.colored_log(f"Observation {step_count}:", observation, color="blue")
        self.logger.log()
        consecutive_think = 0
        repeated_think = 0
        last_think = ''
        self.plans = []
        subgoal_done = True
        subgoal_step = 0
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
                epi_history = f'Observation: {last_non_think}\n'
                consecutive_think = 0

            full_prompt = self.construct_prompt(traj = epi_history, # traj = '' to disable history
                                                plan = plan)
            # print(full_prompt)
            # st()
            action = self.get_action(full_prompt, max_tokens=256, stop=['\nObservation', '\nAction: '])

            if action.startswith('Action:'):
                action = action.split('Action:')[1]

            if action == 'stop':
                self.logger.colored_log(f"Action {step_count}:", 'stop', color="blue")
                subgoal_done = True
                subgoal_step = 0
                continue

            subgoal_step += 1
            self.log_frame(action, i)
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()):
                break

            if action.startswith('think') or action.startswith('<think>'):
                action = action.split(']')[0] + ']'
                observation = 'OK.'
                consecutive_think += 1
                if action == last_think:
                    repeated_think += 1
            else:
                # st()
                consecutive_think = 0
                repeated_think = 0
                try:
                    observation, reward, done, info = self.env.step(action)
                    last_non_think = observation
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

            self.logger.colored_log(f"Action {step_count}:", action, color="blue")
            self.logger.colored_log(f"Observation {step_count+1}:", observation, color="blue")
            self.logger.log()
            
        epi_history = '\nObservation:'.join(epi_history.split('\nObservation:')[:-1])
        if not done:
            epi_history += f'\nObservation: Maximum Step Exceeded, task failed. '
        if reward == 1:
            epi_history += f'\nObservation: Task completed successfully.'

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