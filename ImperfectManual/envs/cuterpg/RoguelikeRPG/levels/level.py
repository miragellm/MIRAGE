"""
Base level class for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from pdb import set_trace as st

class Level(ABC):
    """
    Abstract base class for all game levels.
    """
    
    def __init__(self, 
                 level_number: int, 
                 level_type: str,
                 reversible=False):
        self.level_number = level_number
        self.level_type = level_type
        self.completed = False
        self.back = False 
        self.description = ""
        self.reversible = reversible
        self.available_actions = []
        self.interactions = {}  # Objects that can be interacted with
        self.renamed_items = {}
    
    @abstractmethod
    def enter(self, player: Player) -> str:
        """
        Called when the player enters this level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the level
        """
        pass
    
    @abstractmethod
    def process_action(self, player: Player, action: str, *args) -> Dict[str, Any]:
        """
        Process a player action in this level.
        
        Args:
            player: The player
            action: The action being taken
            args: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        pass


    def process_general_action(self, player: Player, action: str, *args):
        if action == "leave":
            can_exit, message = self.can_exit(player)
            if can_exit:
                return self.exit(player)
            else:
                return {"success": False, "message": message}
            
        elif action == 'back':
            if not self.reversible:
                return {"success": False, "message": 'you can not go back.'}
            
            can_go_back, message = self.can_go_back(player)
            if can_go_back:
                return self.go_back(player)
            else:
                return {"success": False, "message": message}
        
        # elif action == "check":
        #     # Check the manual or other game info
        #     if len(args) > 0:
        #         section = args[0]
        #         return self.check_manual(section)
        #     else:
        #         return self.check_manual()
                
        elif action == "craft":
            # Craft an item (now available in all levels)
            if len(args) == 0:
                return {"success": False, "message": "Craft what? Try 'craft [item name]'"}
            
            item_name = args[0]
            success, message, crafted_item = CraftingSystem.craft_item(player.inventory, item_name)
            
            if success:
                # Add some flavor text
                flavor_texts = [
                    "The materials combine perfectly, forming ",
                    "With skillful crafting, you create ",
                    "The elements respond to your touch, becoming ",
                    "After careful work, you've successfully crafted ",
                    "The crafting process goes smoothly, resulting in "
                ]
                
                flavor = random.choice(flavor_texts)
                return {"success": True, "message": f"{flavor}{item_name}! {message}"}
            else:
                return {"success": False, "message": message}

        elif action == "recipes":
            # View all available crafting recipes
            # Get all recipes
            all_recipes = CraftingSystem.get_all_recipes()
            
            # Update available recipes
            available_recipes = CraftingSystem.get_available_recipes(player.inventory)
            
            # Create a formatted list of recipes
            recipes_by_category = {
                "Weapons": [],
                "Enhancers": [],
                "Advanced Weapons": []
            }
            
            for item_name, recipe_desc in all_recipes.items():
                # Categorize the recipe
                if "Enhancer" in item_name:
                    category = "Enhancers"
                elif any(advanced in item_name for advanced in ["Inferno", "Tsunami", "Gaia", "Divine", "Void", "Storm", "Glacier", "Mountain"]):
                    category = "Advanced Weapons"
                else:
                    category = "Weapons"
                
                # Check if it's available
                available = item_name in available_recipes
                status = "[Available]" if available else "[Missing materials]"
                
                recipes_by_category[category].append(f"- {item_name}: {recipe_desc} {status}")
            
            # Format the complete recipe book
            content = "# Crafting Recipe Book\n\n"
            
            for category, recipes in recipes_by_category.items():
                if recipes:
                    content += f"## {category}\n"
                    content += "\n".join(recipes)
                    content += "\n\n"
            
            return {
                "success": True,
                "message": "You review the crafting recipes you know...",
                "content": content
            }
        
        elif action == "equip":
            if len(args) == 0:
                return {"success": False, "message": "Equip what? Try 'equip [weapon name]'"}
            weapon_name = args[0]
            success, message = player.equip_weapon(weapon_name)
            
            return {"success": success, "message": message}
        
        elif action == 'unequip':
            success, message = player.unequip_weapon()
            return {"success": success, "message": message}
        
        elif action == "discard":
            if len(args) == 0:
                return {"success": False, "message": "Discard what? Try 'discard [item name]'"}
            
            item_name = args[0]
            return self._discard_item(player, item_name)
        
        else:
            return {"success": False, "message": f"Invalid action: {action}. Try one of: {', '.join(self.available_actions)}"}

    
    @abstractmethod
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        pass

    def can_go_back(self, player):
        if self.level_number == 1:
            return False, "You're already at the first level — there's nowhere to go back."
        return True, "You can return to the previous level."
    
    def go_back(self, player):
        self.back = True
        self.completed = False
        return {
            "success": True,
            "message": f"You go back to the last level."
        }
    
    def exit(self, player: Player) -> Dict[str, Any]:
        """
        Called when the player exits this level.
        
        Args:
            player: The player exiting the level
            
        Returns:
            Dict[str, Any]: Result of exiting the level
        """
        self.completed = True
        return {
            "success": True,
            "message": f"You leave the {self.level_type} level."
        }
    
    def get_level_info(self) -> Dict[str, Any]:
        """
        Get information about the current level.
        
        Returns:
            Dict[str, Any]: Level information
        """
        return {
            "level_number": self.level_number,
            "level_type": self.level_type,
            "description": self.description,
            "completed": self.completed,
            "available_actions": self.available_actions,
            "interactions": list(self.interactions.keys())
        }
        
    def _collect_item(self, player: Player, item_name: str) -> Dict[str, Any]:
        """Collect an item from the level."""
        # Check if the item exists and can be collected
        # if item_name not in self.collectibles:
        #     return {"success": False, "message": f"There is no {item_name} to collect here."}
        if item_name in self.renamed_items:
            return {"success": False, "message": f"There is no {item_name} to collect here."}

        if item_name not in self.collectibles:
            matched_key = False
            for name, entry in self.collectibles.items():
                item = entry.get("item") if isinstance(entry, dict) else entry
                if item and item.display_name == item_name:
                    item_name = name
                    matched_key = True
                    break

            if not matched_key:
                return {"success": False, "message": f"There is no {item_name} to collect here."}
        
        collectible = self.collectibles[item_name]
        item = collectible["item"]
        
        # Try to add to the player's inventory
        success, message = player.add_to_inventory(item)
        
        if success:
            # Remove from the level
            del self.collectibles[item_name]
            if item_name in self.interactions:
                del self.interactions[item_name]
            return {"success": True, "message": f"You collected the {item_name}. {message}"}
        else:
            return {"success": False, "message": message}
    
    def _get_common_actions(self) -> List[str]:
        """
        Get the list of actions that are common to all levels.
        
        Returns:
            List[str]: List of common actions
        """
        return [
            "leave",   # Go to the next level
            "craft",   # Craft items (available everywhere now)
            "recipes", # View available recipes
            'discard',
            'equip',
            'unequip',
            'back',
        ]
        
    def _discard_item(self, player: Player, item_name: str) -> Dict[str, Any]:
        """Discard an item from the player's inventory."""
        if item_name in self.renamed_items:
            return {"success": False, "message": f"Item '{item_name}' not found in inventory"}

        for key, value in self.renamed_items.items():
            if item_name == value:
                item_name = key
                break
        success, message = player.inventory.remove_item(item_name)
        
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    
    # def check_manual(self, section: str = None) -> Dict[str, Any]:
    #     """
    #     Check the game manual for information.
        
    #     Args:
    #         section: The specific section to check, or None for the table of contents
            
    #     Returns:
    #         Dict[str, Any]: The result of checking the manual
    #     """
        
    #     manual = ImperfectManual()
        
    #     if section:
    #         content = manual.get_section(section)
    #         return {
    #             "success": True,
    #             "message": f"You check the manual section on '{section}'",
    #             "content": content
    #         }
    #     else:
    #         toc = manual.get_table_of_contents()
    #         return {
    #             "success": True,
    #             "message": "You check the manual's table of contents",
    #             "content": toc
    #         }
    
    def get_available_items_description(self) -> str:
        """
        Get a description of all available items in this level.
        
        Returns:
            str: A description of available items
        """
        items_description = []
        
        # Check if this is a level with collectibles
        if hasattr(self, 'collectibles') and self.collectibles:
            items_description.append("\nCollectible Items:")
            for item_name, item_info in self.collectibles.items():
                if "item" in item_info:
                    item = item_info["item"]
                    # element_str = f" ({item.element.value})" if item.element else ""
                    element_str = ''
                    if str(item) not in item_info['description']:
                        item_info['description'] = item_info['description'].replace(item_name, str(item))
                    items_description.append(f"- {str(item)}{element_str}: {item_info['description']}")
        
        # Check if this is a level with containers
        if hasattr(self, 'containers') and self.containers:
            items_description.append("\nContainers:")
            for container_name, container_info in self.containers.items():
                if not container_info.get("opened", False):
                    items_description.append(f"- {container_name}: {container_info['description']}")
                else:
                    items_description.append(f"- {container_name}: Already opened")
        
        # Check if this is a level with NPCs
        if hasattr(self, 'npcs') and self.npcs:
            items_description.append("\nNPCs:")
            for npc_name, npc_info in self.npcs.items():
                items_description.append(f"- {npc_name}: {npc_info['description']}")
        
        # Check if this is a level with readables
        if hasattr(self, 'readables') and self.readables:
            items_description.append("\nReadable Objects:")
            for readable_name, readable_info in self.readables.items():
                items_description.append(f"- {readable_name}: {readable_info['description']}")
        
        # Check if this is a level with an enemy
        if hasattr(self, 'enemy') and self.enemy:
            items_description.append("\nEnemy:")
            element_str = f" ({self.enemy.element.value})" if hasattr(self.enemy, 'element') else ""
            items_description.append(f"- {self.enemy.name}{element_str}")
        
        # Check if this is a shop level
        if hasattr(self, 'for_sale') and self.for_sale:
            items_description.append("\nItems For Sale:")
            for item_name, item_info in self.for_sale.items():
                item = item_info["item"]
                element_str = f" ({item.element.value})" if item.element else ""
                price_str = ", ".join([f"{count} {name}" for name, count in item_info["price"]])
                if str(item) not in item_info['description']:
                    item_info['description'] = item_info['description'].replace(item_name, str(item))
                items_description.append(f"- {str(item)}{element_str}: {item_info['description']} (Costs: {price_str})")
        
        if not items_description:
            return ""
        
        return "\n" + "\n".join(items_description)
    
    def get_available_item_names(self) -> List[str]:
        """
        Get the names of all currently available items in this level.
        
        Returns:
            List[str]: Names of all items that can be picked up or obtained
        """
        available_items = []

        # From collectibles
        if hasattr(self, 'collectibles') and self.collectibles:
            for item_name, item_info in self.collectibles.items():
                if "item" in item_info:
                    available_items.append(item_name)

        # From unopened containers that actually contain items
        if hasattr(self, 'containers') and self.containers:
            for container_info in self.containers.values():
                if not container_info.get("opened", False):
                    item = container_info.get("item", None)
                    if item:
                        available_items.append(item.name)

        # From shops
        if hasattr(self, 'for_sale') and self.for_sale:
            for item_name in self.for_sale:
                available_items.append(item_name)

        # From enemy drops
        if hasattr(self, 'enemy') and self.enemy:
            if hasattr(self.enemy, 'drops') and self.enemy.drops:
                for item in self.enemy.drops:
                    if isinstance(item, str):
                        available_items.append(item)
                    else:
                        available_items.append(item.name)

        return available_items
    
    def __str__(self) -> str:
        """String representation of the level."""
        return f"Level {self.level_number}: {self.level_type.capitalize()}"
    
    
    def print_level(self):
        return