import copy
from typing import Dict, Any, List, Optional, Tuple
from common.llms import llm
from .game import Game
from .constants import GameMode
from pdb import set_trace as st

class Env:
    """
    Core environment class for RPG game, handling game state, 
    level progression, and player interactions.
    """
    
    def __init__(self, 
                 mode: str = "easy",
                 shuffle_container = False,
                 single_level_enemy = 1,
                 shuffle_enemy = False,
                 reversible = False,
                 item_rename = False):
        """
        Initialize the RPG environment.
        
        Args:
            mode: Game mode ("easy" or "hard")
            seed: Random seed for reproducibility
        """
        # Parse mode
        self.mode = GameMode.EASY if mode.lower() == "easy" else GameMode.HARD
        self.shuffle_container = shuffle_container
        self.single_level_enemy = single_level_enemy
        self.shuffle_enemy = shuffle_enemy
        self.reversible = reversible
        self.item_rename = item_rename

        # Define action space
        self.available_actions = [
            "attack", "equip", "collect", "open", "talk", "read", 
            "buy", "craft", "recipes", "analyze", "discard", 
            "leave", "think", "check", "inventory", "status", 'unequip', 'back'
        ]
        

    def reset(self) -> str:
        """
        Reset the environment to the initial state.
        
        Returns:
            str: Initial observation
        """
        # Reinitialize the game
        self.game = Game(mode=self.mode,
                         shuffle_container=self.shuffle_container,
                         single_level_enemy=self.single_level_enemy,
                         shuffle_enemy=self.shuffle_enemy,
                         reversible=self.reversible,
                         item_rename=self.item_rename)
        
        self.initial_game = copy.deepcopy(self.game)

        return self.reset_void()
        
    
    def reset_void(self):
        # Reset state
        self.done = False
        self.last_reward = 0
        
        # Get initial observation
        self.observation = self.game.start()
        self.observation += f'Your current HP: {self.game.player.current_hp}.'
        self.game.get_current_level().print_level()
        
        self.last_hp = self.game.player.current_hp
        self.last_inventory = str(self.game.player.inventory)
        return self.observation

    
    def take_action(self, action_text: str) -> Tuple[str, float, bool, Dict[str, Any]]:
        """
        Process an action in the environment.
        
        Args:
            action_text: The action to take (e.g., "equip sword", "collect potion")
            
        Returns:
            Tuple containing:
            - observation (str): Text description of the new state
            - reward (float): Reward for the action
            - done (bool): Whether the episode is complete
            - info (dict): Additional information
        """
        # Parse action and arguments
        parts = action_text.strip().split(' ', 1)
        action = parts[0].lower()
        args = []
        reward = 0
        
        if len(parts) > 1:
            arg_text = parts[1].strip()
            # Remove brackets if present
            if arg_text.startswith('[') and arg_text.endswith(']'):
                arg_text = arg_text[1:-1].strip()
            args = [arg_text]
        
        # Check if action is valid
        if action not in self.available_actions:
            observation = f"Invalid action: {action}. Available actions: {', '.join(self.available_actions)}"
            return observation, 0, self.done, {}
        
        # Process the action
        result = self.game.process_action(action, *args)
        
        # Update observation
        observation = result["message"]
        if "content" in result:
            observation += f"\n\n{result['content']}"
        
        # Check if episode is done
        curr_level = self.game.get_current_level()
        if curr_level.level_type == 'boss':
            if curr_level.is_final_boss:
                if result.get('victory', False):
                    reward = self.game.player.current_hp/self.game.player.max_hp
                    self.done = True
            elif result.get('battle_over', False) and not result.get('victory', True):
                self.done = True 

        elif self.game.get_current_level().level_type == 'combat':
            if result.get('battle_over', False) and not result.get('victory', True):
                self.done = True
        
        # Additional info
        info = {k: v for k, v in result.items() if k not in ["message", "content"]}
        info["game_state"] = self.game.get_game_state()
        
        
        if self.game.player.current_hp != self.last_hp:
            observation += f'\nYour current HP: {self.game.player.current_hp}'
            self.last_hp = self.game.player.current_hp

        if str(self.game.player.inventory) != self.last_inventory:
            observation += f'\n{str(self.game.player.inventory)}'
            self.last_inventory = str(self.game.player.inventory)
            
        self.observation = observation
        self.last_reward = reward
        self.game.get_current_level().print_level()
        
        return self.observation, reward, self.done, info
    
    
    def get_available_actions(self) -> List[str]:
        """
        Get list of available actions in current state.
        
        Returns:
            List[str]: Available actions
        """
        if not self.done:
            return self.game.get_current_level().available_actions
        return []
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        
        Returns:
            Dict[str, Any]: Current state
        """
        return self.game.get_game_state()
    
    def get_manual(self, manual_type: Optional[str] = None) -> str:
        """
        Get a manual or help text for the environment.
        
        Args:
            manual_type
            
        Returns:
            str: Manual text
        """
        manual_text = self.game.solution_manager.get_solution_path(manual_type)
        self.apply_dynamics()
        return manual_text
    
    
    def apply_dynamics(self):
        self.game.apply_dynamics()

