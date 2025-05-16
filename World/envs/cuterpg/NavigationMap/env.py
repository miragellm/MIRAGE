# RL_environment.py
import re
import random
import copy 
import numpy as np
from .observation import encode_obs
from .path_converter import convert_path_to_instructions
from pdb import set_trace as st

class Env:
    def __init__(self, game_map, 
                       character, 
                       npc_manual_lst,
                       max_rounds=30, 
                       obs_type='raw',
                       ):
        self.game_map = game_map
        self.character = character
        self.max_rounds = max_rounds
        self.num_rounds = 0
        self.last_obs = None
        self.obs_type = obs_type
        self.npc_manual_lst = npc_manual_lst
        self.initial_map = None
        self.initial_character= None 

    def reset(self):
        self.game_map.reset()
        self.character.reset()
        self.initial_map = copy.deepcopy(self.game_map.map_data)
        self.num_rounds = 0
        return self.character.get_observation()
    

    def goal_completed(self):
        # at the cloest road to the destimation
        closet = self.game_map.closet_to_goal_tiles()
        return self.character.position in closet
    
    def take_action(self, action):
        reward = 0
        action = action.strip()
        if action not in ['reset', 'void']:
            self.game_map.step_before()
            
        # print(f'current action:{action}\n')
        if action in ['forward', 'turn left', 'turn right', 'turn around']:
            self.character.move(action)
            raw_obs = self.character.get_observation()
            if self.obs_type == 'raw':
                next_obs = self.matrix_to_string(raw_obs)
            elif self.obs_type == 'encoded':
                next_obs = self.encode_obs(raw_obs)
            next_obs += f"\nDirection: You are facing {self.character.direction}."
        elif action == "reset":
            raw_obs = self.reset()
            if self.obs_type == 'raw':
                next_obs = self.matrix_to_string(raw_obs)
            elif self.obs_type == 'encoded':
                next_obs = self.encode_obs(raw_obs)
            next_obs += f"\nDirection: You are facing {self.character.direction}."
        elif action == "wait": 
            next_obs = self.last_obs
            raw_obs = self.character.get_observation()
        elif action == 'void':
            raw_obs = self.character.get_observation()
            if self.obs_type == 'raw':
                next_obs = self.matrix_to_string(raw_obs)
            elif self.obs_type == 'encoded':
                next_obs = self.encode_obs(raw_obs)
            next_obs += f"\nDirection: You are facing {self.character.direction}."
        elif action == 'inquire_npc':
            manual_type = random.choice(self.npc_manual_lst)
            raw_obs = self.game_map.get_npc_manual(manual_type, self.character.position, self.character.direction)
        else:
            next_obs = "Wrong action format: you can only choose from these actions: forward, turn left, turn right, turn around, or think[...]."
            
        if action not in ['reset', 'void']:
            self.game_map.step_after(self.character.position)
            
        self.num_rounds += 1
        done = self.goal_completed()
        if self.num_rounds >= self.max_rounds:
            done = True
            
        if done:
            dist = self.game_map.dist_to_goal(self.character.position)
            reward = 1 - (dist/(self.game_map.MAP_ROWS + self.game_map.MAP_COLS))

        info = {}
        if action == 'forward' and self.last_obs == next_obs:
            info['warning'] = 'Warning: The tile in front of you is not a 6x6 road tile, causing your forward action to fail. Please try a different action.'
            next_obs = "Cannot move forward: your front tile is not road."
        else:
            self.last_obs = next_obs

        return next_obs, reward, done, info

    def gt_instructions(self):
        """Steps"""
        return convert_path_to_instructions(self.game_map.path)

    def descriptive_manual(self):
        return self.game_map.gt_manual

    def matrix_to_string(self, matrix):
        return '\n'.join([' '.join(row) for row in matrix])
    
    def string_to_matrix(self, matrix_str):
        return [line.strip().split() for line in matrix_str.strip().split('\n')]

    def encode_obs(self, matrix):
        obs = encode_obs(matrix,
                         self.game_map.season,
                         include_void=True,
                         include_small_items=True,
                         )
        obs = '\n'.join(obs)
        return obs