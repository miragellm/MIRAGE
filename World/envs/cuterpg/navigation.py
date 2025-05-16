# visulization.py
import gym
import pygame
from .utils.config import TILE_SIZE
from .utils.charactersprite import CharacterSprite
from .NavigationMap.navigationMap import GameMap
from .NavigationMap.main_character import NavigationCharacter
from .NavigationMap.env import Env
from pdb import set_trace as st

class NavigationEnv(gym.Env):
    def __init__(self, **kwargs):
        super(NavigationEnv, self).__init__()
        
        self.obs_type = kwargs["obs_type"]
        self.mode = kwargs.get("mode", 'hard')
        self.seasons = kwargs.get("seasons", ["summer"])
        self.dynamic = kwargs.get("dynamic", False)
        self.npc = kwargs.get("npc", 0)
        npc_manual_lst = kwargs.get('npc_manual_lst', [1, 2])
        construction = kwargs.get('construction', False)
        window_width = kwargs.get('window_width', 600)
        window_height = kwargs.get('window_height', 600)
        max_land_size = kwargs.get('max_land_size', 4)
        min_land_size = kwargs.get('min_land_size', 2)
        map_rows = kwargs.get('map_rows', 12)
        map_cols = kwargs.get('map_cols', 12)
        
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Navigation Map")

        self.character_sprite = CharacterSprite()
        self.game_map = GameMap(self.screen,
                                self.seasons,
                                self.dynamic,
                                self.npc,
                                self.mode,
                                construction,
                                max_land_size=max_land_size,
                                min_land_size=min_land_size,
                                map_rows=map_rows,
                                map_cols=map_cols,
                                )
        self.character = NavigationCharacter(self.character_sprite, self.game_map, step_size=TILE_SIZE)
        self.env = Env(self.game_map, self.character, npc_manual_lst, obs_type=self.obs_type)
    
    def record_initial(self):
        self.initial_pos = self.character.position
        self.initial_dir = self.character.direction

    def reset(self):
        done = True
        while done:
            # in case a task diectly succeeds
            obs, reward, done, info = self.env.take_action('reset')
        self.update_screen()
        self.switch_season()
        # need to get the observation here in case the season is changed
        obs, reward, done, info = self.env.take_action('void')
        self.record_initial()
        self.update_screen()
        return obs
    
    def rewind(self):
        # go back to the initial state
        self.character.position = self.initial_pos
        self.character.direction = self.initial_dir
        obs, reward, done, info = self.env.take_action('void')
        return obs, reward, done, info
    
    def back_to_start(self):
        self.env.game_map.map_data = self.env.initial_map
        # self.character = self.initial_character
        self.env.num_rounds = 0
        obs = self.rewind()[0]
        self.update_screen()
        return obs

    def get_horizon(self):
        return self.game_map.max_horizon

    def step(self, action):
        obs, reward, done, info = self.env.take_action(action)
        self.update_screen()
        return obs, reward, done, info
    
    def get_gt_mode(self):
        status = self.env.game_map.get_map_manual_status(self.character.position,
                                       self.character.direction)
        return status
    
    def switch_season(self):
        self.game_map.switch_season()

    def update_screen(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw()
        self.character.draw(self.screen)
        pygame.display.flip()

    def get_manual(self, manual_type):
        if manual_type is None:
            return '', ''
        manual, imperfect_info = self.env.game_map.get_manual(manual_type)
        # for this specific manual, let's generate gt mode map
        return manual, imperfect_info
    
