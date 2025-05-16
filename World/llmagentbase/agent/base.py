import re
from common.llms import llm, token_num
from pdb import set_trace as st


class Agent:
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    ):
        self.env = env
        self.instruction = instruction
        self.in_context = in_context
        self.logger = logger
        self.model_name = model_name
        self.temperature = temperature
    
    def format_action(self, action):
        action_splitter = "```"
        pattern = rf"{action_splitter}((.|\n)*?){action_splitter}"
        match = re.findall(pattern, action, re.DOTALL)
        if match:
            # action = match[-1][0]
            action = match[0][0] 
            # action = f'unable to parse the action, please make sure to put it inside ``````. Here is the last action you generated: {action_record}'
            action = action
        return action
    
    def epi_no_thinking(self,
                        traj):
        result = ''
        all_lines = traj.split('\n')
        idx = 0 
        while idx < len(all_lines):
            line = all_lines[idx]
            if line.startswith('Action: think['):
                idx += 3
            else:
                result += f'{line}\n'
                idx += 1
        return result[:-1]
    
    def get_action(self, prompt, max_tokens, stop, reset_context=False):
        print(token_num(prompt))
        action = llm(prompt,
                     model_name=self.model_name,
                     temperature=self.temperature,
                     max_tokens=max_tokens,
                     stop=stop,
                     reset_context=reset_context)
        if action is None: action = ''
        action = action.replace('\n', ' ').strip()
        return action
    
    def skip_env(self):
        return
    
    def close_env(self):
        return

    def construct_prompt(self,
                         reflection,
                         traj,
                        ):
        raise NotImplementedError("You need to implement a prompt constructor. ")
    
    def step(self, 
             action,
             reward=0,
             done=False,
             info={}):
        if action.startswith('think'):
            observation = 'OK.'
        else:
            try:
                observation, reward, done, info = self.env.step(action)
            except AssertionError as e:
                self.logger.log(f"[red][Error][/]: {e}", option='console')
                observation = f'Invalid action! '
        return observation, reward, done, info
        
    
    def run(self, 
            task_name,
            trial, 
            reflection,
            args=None):
        raise NotImplementedError("You need to implement a function to generate actions and interact with the environment. ")
