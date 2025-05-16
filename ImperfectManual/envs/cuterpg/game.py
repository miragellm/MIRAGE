import gym
from .RoguelikeRPG.env import Env
from pdb import set_trace as st

class GameEnv(gym.Env):
    """
    Gym-compatible environment wrapper for the RPG game.
    Provides a standard RL interface.
    """

    def __init__(self, **kwargs):
        """
        Initialize the game environment.
        
        Args:
            **kwargs: Keyword arguments passed to Env
        """
        super(GameEnv, self).__init__()
        self.mode = kwargs.get("mode", 'easy')
        self.shuffle_container = kwargs.get("shuffle_container", False)
        self.single_level_enemy = kwargs.get("single_level_enemy", 1)
        self.shuffle_enemy = kwargs.get("shuffle_enemy", False)
        self.reversible = kwargs.get("reversible", False)
        self.item_rename = kwargs.get("item_rename", False)
        self.env = Env(self.mode,
                       shuffle_container=self.shuffle_container,
                       single_level_enemy=self.single_level_enemy,
                       shuffle_enemy=self.shuffle_enemy,
                       reversible=self.reversible,
                       item_rename=self.item_rename)

    def step(self, action):
        """
        Take a step in the environment.
        
        Args:
            action: Action to take (string)
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        obs, reward, done, info = self.env.take_action(action)
        return obs, reward, done, info

    def reset(self):
        """
        Reset the environment.
        
        Returns:
            Initial observation
        """
        return self.env.reset()
    
    def back_to_start(self):
        self.env.game = self.env.initial_game
    
    def render(self, mode='human'):
        """
        Render the environment.
        
        Args:
            mode: Rendering mode
        """
        print(self.env.observation)
        
    def get_status(self):
        inventory = f"Your current inventory:\n{self.env.game.player.inventory}\n\n"
        level = self.env.game.get_current_level()
        obs = level.get_curr_obs()
        return f"{inventory}You are at Level {level.level_number}: \n{obs}"
    
    def close(self):
        """Clean up resources."""
        pass
    
    def get_manual(self, manual_type=None):
        """
        Get a manual for the environment.
        
        Args:
            manual_type: Type of manual to retrieve
            
        Returns:
            Tuple of (manual_text, additional_info)
        """
        manual = self.env.get_manual(manual_type)
        obs = self.env.reset_void()
        return obs, manual
    
    def get_horizon(self):
        if self.mode == 'easy':
            return 100 # this includes thinking steps
        elif self.mode == 'hard':
            return 150