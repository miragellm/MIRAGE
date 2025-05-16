import numpy as np
from .base import Agent
from llmagentbase.utils import plan_to_str
from pdb import set_trace as st


plan_prompt = """In this task, you will play through a turn-based roguelike RPG with the goal of defeating the final-floor boss.

You can only issue the following actions in this environment, one at a time:
    think[...]                -> Private reasoning or planning (the environment echoes back “OK.”). Do not overuse it. Specifically, you cannot think with similar output multiple times, which causes useless duplication.
    collect <item>            -> Pick up a listed collectible item.
    open <container>          -> Open a container and automatically scoop up its contents.
    craft <item>              -> Combine the exact required materials in your inventory.
    discard <item>            -> Drop an item to free weight.
    unequip                   -> for all environments
    equip <weapon>            -> Wield a weapon from your inventory.
    attack <enemy>            -> Strike the target (must have a weapon equipped).
    buy <item>                -> Purchase from a shop if you meet the cost.
    talk <npc>                -> Speak with an NPC.
    read <object>             -> Read flavour or clue text.
    leave                     -> Exit the current level and advance to the next.
    recipes                   -> Show a list of available crafting recipes.

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

Here are some example subgoals:
- Collect one Fire Essence, craft Fire Staff and discard unnecessary materials.
- Collect Water Crystal and Fire Essence in this level and then leave.
- leave level 1
- equip Fire Staff and beat Restless Rain Phantom
- Craft Inferno Blaster then go to level 6.

Here is an example:
Step-by-Step Guide to Complete the Task: 
You will face a ICE-element boss on the final floor.
To counter it effectively, we recommend using a FIRE-element weapon: Inferno Blaster.

To craft Inferno Blaster, follow these steps:
- Craft Fire Staff using 1 Fire Essence, 1 Weapon Prototype
- Craft Fire Enhancer using 2 Fire Essence, 1 Magic Catalyst
- Craft Inferno Blaster using 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth

Make sure that you have the following items in your inventory when you leave each of the levels:
  Level 1 (growth):
    - Fire Staff ×1
    - Magic Catalyst ×1
  Level 2 (growth):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
  Level 3 (combat):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
    - Enchanted Cloth ×1
  Level 4 (growth):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
    - Enchanted Cloth ×1
  Level 5 (shop):
    - Inferno Blaster ×1

Trajectory:
Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: think[The strategy guide says I must leave this level with a *Fire Staff*. That requires 1 Fire Essence + my Weapon Prototype. Step 1: pick up Fire Essence.]
Observation: OK.

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.

Action: think[I need to collect a Magic Catalyst to pass the checkpoint. However, there is no Magic Catalyst, I will open the containers one by one to check if Magic Catalyst is inside. If other junks are inside I will just discard them.]
Observation: OK.

Action: open bird nest
Observation: You found **Magic Catalyst**! Added to inventory.

Action: think[Now craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Past plans: 
1. find and collect Magic Catalyst.
2. find Fire Essence and craft Fire Staff

Reasoning: Now I have gathered required materials at the current level. I can discard unnecessary items and leave the current level.
Next plan step: discard Frost Particle and leave the current level. 

Now it's your turn: 
Step-by-Step Guide to Complete the Task: 
{guide}

Trajectory:
{traj}

Past plans: 
{plans}

Reasoning: """

class GamePlanner(Agent):
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
        self.action_stats = {}
        self.available_actions = []
        self.mode_recs = []

    def construct_prompt(self, traj, plan):
        prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn: \nA guide that contains important information:{self.manual}\n\nCurrent subgoal: {plan}\nTrajectory:\n"
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

        observation = self.env.reset()
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
                    self.logger.colored_log(f"Level obs:", self.env.get_status(), color="blue")
                else:
                    epi_history = f'Observation: {last_non_think}\n'
                consecutive_think = 0
                subgoal_step = 0

            # Get available actions from the info dictionary
            available_actions_text = self.process_game_info(info)
            

            if available_actions_text:
                full_prompt = self.construct_prompt(traj = epi_history + f"\nAvailable actions: {available_actions_text}\n", plan = plan)
            else:
                full_prompt = self.construct_prompt(traj = epi_history, plan = plan)


            action = self.get_action(full_prompt, max_tokens=256, stop=["Observation:", "\nAction: "])
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()):
                break
            
            if action.startswith('Action:'):
                action = action.split('Action:')[1]

            if action.startswith('stop'):
                self.logger.colored_log(f"Action {step_count}:", 'stop', color="blue")
                subgoal_done = True
                subgoal_step = 0
                continue
            
            subgoal_step += 1

            if action.startswith('Action:'):
                action = action.split('Action:')[1]

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
            
            if subgoal_step >= 15:
                action == '\nWarning: This subgoal exceeds the 10-step limit.'
                subgoal_done = True
                subgoal_step = 0

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
        self.logger.log(f"Total Reward: {reward}")
        self.logger.log(f"Total Steps: {step_count}")
        self.logger.log(f"Actions Used: {self.action_stats}")
        # st()
        
        return reward, epi_history, step_count