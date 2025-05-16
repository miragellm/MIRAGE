"""
Main game manager for the RougelikeRPG game.
"""
import copy
import random
import numpy as np
from typing import List, Dict, Any
from envs.cuterpg.RoguelikeRPG.constants import GameMode, Element, EASY_MODE_LAYERS, HARD_MODE_LAYERS, BASE_MATERIALS, RENAME_MAP
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.item import create_material, Item
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.levels.growth_level import GrowthLevel
from envs.cuterpg.RoguelikeRPG.levels.combat_level import CombatLevel
from envs.cuterpg.RoguelikeRPG.levels.boss_level import BossLevel
from envs.cuterpg.RoguelikeRPG.levels.shop_level import ShopLevel
from envs.cuterpg.RoguelikeRPG.utils.solution_manager import SolutionManager
from envs.cuterpg.RoguelikeRPG.levels.utils import add_item
from envs.cuterpg.RoguelikeRPG.utils.utils import derangement
from pdb import set_trace as st

def generate_hint_text(original, renamed):
    """Generate a flavor-style hint line for a renamed item."""
    templates = [
        f"Some folks call it '{renamed}' these days... but it's really just '{original}'.",
        f"The locals speak of '{renamed}', but it works the same as '{original}'.",
        f"Old texts refer to '{renamed}'—a fancy name for good old '{original}'.",
        f"Don't be fooled by the name '{renamed}'. It's basically '{original}' with flair.",
        f"They renamed '{original}' as '{renamed}', but it still holds the same essence.",
    ]
    return random.choice(templates)

class Game:
    """
    Main game manager that handles game state, level progression,
    and player interactions.
    """
    
    def __init__(self, 
                 mode: GameMode = GameMode.EASY,
                 shuffle_container=False,
                 single_level_enemy=1,
                 shuffle_enemy=False,
                 reversible=False,
                 item_rename=False):
        """
        Initialize a new game.
        
        Args:
            mode: Game mode (EASY or HARD)
        """
        self.mode = mode
        self.player = Player()
        self.current_level_index = 0
        self.levels: List[Level] = []
        self.game_completed = False
        self.game_over = False

        self.shuffle_container = shuffle_container
        self.single_level_enemy = single_level_enemy
        self.shuffle_enemy = shuffle_enemy
        self.reversible = reversible
        self.item_name = item_rename

        # Initialize starting inventory with random items
        self._initialize_player_inventory()
        
        # Generate the game levels
        self._generate_levels()
        self.reset_player_hp()
        return
    
    def apply_dynamics(self):
        self.shuffle_items()
        self.apply_renames()

    def apply_renames(self):
        if not self.item_name:
            return

        # -----------------------------
        # Step 1: Sample renamed subset and assign aliases
        # -----------------------------
        # --- Step 0: Identify actually required items in recipe ---
        # We'll assume self.required_items exists and is populated (dict[str → count])
        required_keys = list(self.solution_manager.required_items.keys())
        random.shuffle(required_keys)

        # Pick up to 2 required items that are also in RENAME_MAP
        renamed_from_required = [k for k in required_keys if k in RENAME_MAP][:1]

        # Then pick additional noise items not in the recipe
        rename_pool = [k for k in RENAME_MAP.keys() if k not in renamed_from_required and k not in self.solution_manager.required_items]
        num_noise = max(0, 3 - len(renamed_from_required))  # total rename count = 4
        noise_keys = random.sample(rename_pool, num_noise)

        # Combine
        selected_keys = renamed_from_required + noise_keys

        # Final renamed_items dict
        self.renamed_items = {
            k: random.choice(RENAME_MAP[k]) for k in selected_keys
        }

        for key, val in self.renamed_items.items():
            print(f"{key} -> {val}")

        # -----------------------------
        # Step 2: Apply display_name to all relevant items
        # -----------------------------
        for level in self.levels:
            level.renamed_items = self.renamed_items
            # Containers
            if hasattr(level, "containers"):
                for container, container_info in level.containers.items():
                    item = container_info.get("item")
                    if item and item.name in self.renamed_items:
                        level.containers[container]['content_description'] = level.containers[container]['content_description'].replace(item.name, self.renamed_items[item.name])
                        item.display_name = self.renamed_items[item.name]

            # Collectibles
            if hasattr(level, "collectibles"):
                for collect_info in level.collectibles.values():
                    item = collect_info.get("item")
                    if item and item.name in self.renamed_items:
                        item.display_name = self.renamed_items[item.name]

            # Shops
            if hasattr(level, "for_sale"):
                for item_info in level.for_sale.values():
                    item = item_info["item"]
                    if item.name in self.renamed_items:
                        item.display_name = self.renamed_items[item.name]

            # Enemies
            if hasattr(level, "enemies"):
                for enemy in level.enemies:
                    for drop in enemy.drops:
                        if isinstance(drop, Item) and drop.name in self.renamed_items:
                            drop.display_name = self.renamed_items[drop.name]
            elif hasattr(level, "enemy") and level.enemy:
                for drop in level.enemy.drops:
                    if isinstance(drop, Item) and drop.name in self.renamed_items:
                        drop.display_name = self.renamed_items[drop.name]

        # -----------------------------
        # Step 3: Add hint lines to NPCs or Readables
        # -----------------------------
        required_renamed = [k for k in self.solution_manager.required_items if k in self.renamed_items]
        noise_hints = [(k, v) for k, v in self.renamed_items.items() if k not in self.solution_manager.required_items]

        used_hint_keys = set()  # track which hints have been inserted

        def gen_hint_text(k, v):
            return generate_hint_text(k, v)

        # --- 2. Assign required hints to NPCs ---
        for level in [lvl for lvl in self.levels if hasattr(lvl, 'npcs') and lvl.npcs]:
            npc_keys = list(level.npcs.keys())
            random.shuffle(npc_keys)

            # Main NPC：all required hints
            main_npc = npc_keys[0]
            texts = [gen_hint_text(k, self.renamed_items[k]) for k in required_renamed]
            full_text = " ".join(texts)
            level.npcs[main_npc]['dialog'] = f"{level.npcs[main_npc]['dialog'][:-1]} {full_text}\""
            used_hint_keys.update(required_renamed)

            # Other NPC：10% possibility to have one hint
            for npc in npc_keys[1:]:
                if random.random() < 0.1 and required_renamed:
                    k = random.choice(required_renamed)
                    v = self.renamed_items[k]
                    level.npcs[npc]['dialog'] = f"{level.npcs[npc]['dialog'][:-1]} {gen_hint_text(k, v)}\""
                    used_hint_keys.add(k)

        # --- 3. Assign required hints to readables ---
        for level in [lvl for lvl in self.levels if hasattr(lvl, 'readables') and lvl.readables]:
            read_keys = list(level.readables.keys())
            random.shuffle(read_keys)

            # Main readable：all required hints
            main_read = read_keys[0]
            texts = [gen_hint_text(k, self.renamed_items[k]) for k in required_renamed]
            full_text = " ".join(texts)
            level.readables[main_read]['content'] = f"{level.readables[main_read]['content'][:-1]} {full_text}\""
            used_hint_keys.update(required_renamed)

            # Other readable：10% possibility to have one hint
            for r in read_keys[1:]:
                if random.random() < 0.1 and required_renamed:
                    k = random.choice(required_renamed)
                    v = self.renamed_items[k]
                    level.readables[r]['content'] = f"{level.readables[r]['content'][:-1]} {gen_hint_text(k, v)}\""
                    used_hint_keys.add(k)

        # --- 4. Assign noise hint to random npc/readable ---
        remaining_noise = [(k, v) for k, v in noise_hints]
        random.shuffle(remaining_noise)

        all_slots = []

        for level in self.levels:
            if hasattr(level, 'npcs'):
                for npc in level.npcs:
                    all_slots.append(("npc", level, npc))
            if hasattr(level, 'readables'):
                for r in level.readables:
                    all_slots.append(("readable", level, r))

        random.shuffle(all_slots)

        for (k, v) in remaining_noise[:3]:  # 3 noises at most
            if not all_slots:
                break
            typ, level, key = all_slots.pop()
            text = gen_hint_text(k, v)
            if typ == "npc":
                level.npcs[key]['dialog'] = f"{level.npcs[key]['dialog']} {text}\""
            else:
                level.readables[key]['content'] = f"{level.readables[key]['content'][:-1]} {text}\""

        # for level in self.levels:
        #     if hasattr(level, 'npcs'):
        #         for npc in level.npcs:
        #             print(level.npcs[npc]['dialog'])
        #     if hasattr(level, 'readables'):
        #         for readable in level.readables:
        #             print('r', level.readables[readable]['content'])
        # st()
        return 

    def shuffle_items(self):
        """
        Shuffle container contents in a random growth level or enemy drops if enabled.
        """
        # -----------------------------
        # 1. Shuffle one growth level's containers
        # -----------------------------
        if self.shuffle_container:
            # Find all growth levels with collectibles or containers
            growth_levels = [lvl for lvl in self.levels if lvl.level_type == "growth"]

            if growth_levels:
                chosen_levels = random.sample(growth_levels, k=2)
                for chosen_level in chosen_levels:
                    # Gather all available items (collectibles + unopened container items)
                    all_items = []
                    for name, info in chosen_level.collectibles.items():
                        all_items.append(info["item"])

                    # Container items
                    for name, info in chosen_level.containers.items():
                        all_items.append(info["item"])

                    if len(all_items) <= 1:
                        continue  # nothing to shuffle

                    # Shuffle all items
                    all_items = derangement(all_items)

                    idx = 0
                    collectibles_size = len(chosen_level.collectibles)
                    chosen_level.collectibles = {}
                    for _ in range(collectibles_size):
                        item = all_items[idx]
                        if item is not None:
                            add_item(item.name, chosen_level.collectibles, chosen_level.theme)
                        idx += 1

                    for container in chosen_level.containers:
                        item = all_items[idx]
                        if item is not None:
                            chosen_level.containers[container] = {
                            "description": f"There's a {container} that might contain something useful.",
                            "opened": False,
                            "content_description": f"You found a {item.name} inside!",
                            "item": item
                            }
                        else:
                            chosen_level.containers[container] = {
                                "description": f"There's a {container} that might contain something useful.",
                                "opened": False,
                                "content_description": "It's empty. Nothing useful inside.",
                                "item": None
                            }
                        idx += 1
        # -----------------------------
        # 2. Shuffle enemy drops
        # -----------------------------
        if self.shuffle_enemy:
            combat_levels = [lvl for lvl in self.levels if lvl.level_type == "combat"]
            chosen_level = random.choice(combat_levels)
           
            enemy_to_old_drops = [e.drops for e in chosen_level.enemies]
            all_items = derangement(all_items)
            for idx, enemy in enumerate(chosen_level.enemies):
                enemy.drops = enemy_to_old_drops[idx]

    
    def _initialize_player_inventory(self):
        """Initialize the player's inventory with some starting items."""
        # Add a random elemental material
        
        possible_materials = list(BASE_MATERIALS.keys())
        
        # Pick a random elemental material
        material_name = random.choice(possible_materials)
        element = BASE_MATERIALS[material_name]
        description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        material = create_material(material_name, description, element)
        self.player.add_to_inventory(material)
        
        # Add a Weapon Prototype
        prototype = create_material("Weapon Prototype", "A universal crafting material used for creating weapons.")
        self.player.add_to_inventory(prototype)
        
        # 50% chance to add a second material
        if random.random() < 0.5:
            # Make sure it's different from the first one
            remaining_materials = [m for m in possible_materials if m != material_name]
            second_material_name = random.choice(remaining_materials)
            element = BASE_MATERIALS[second_material_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            second_material = create_material(second_material_name, description, element)
            self.player.add_to_inventory(second_material)
            
        # print(f"[INIT] Inventory after initialization:\n{self.player.inventory}")
        return 
    
    def _generate_levels(self):
        """Generate all levels for the game based on the selected mode."""
        # Determine the level sequence based on game mode

        if self.mode == GameMode.EASY:
            level_types = EASY_MODE_LAYERS
        else:
            level_types = HARD_MODE_LAYERS
        
        # Plan enemy elements to ensure variety and progression
        all_elements = list(Element)
        boss_element = random.choice(all_elements)
        
        # For hard mode, also plan a mini-boss element different from the final boss
        if self.mode == GameMode.HARD:
            miniboss_element_options = [e for e in all_elements if e != boss_element]
            miniboss_element = random.choice(miniboss_element_options)
        else:
            miniboss_element = None
        
        # Create levels based on the sequence
        self.levels = []
        next_enemy_type = None  # Track the next enemy type for hints
        
        for i, level_type in enumerate(level_types):
            level_number = i + 1
            # print("Random check:", random.random(), np.random.rand())
            
            # Determine next enemy type for hints
            if i < len(level_types) - 1:
                next_type = level_types[i + 1]
                if next_type == "combat":
                    # Generate a random enemy type for hint
                    element = random.choice(all_elements)
                    #element = boss_element
                    print(f"current element:{element}")
                    from envs.cuterpg.RoguelikeRPG.constants import ENEMY_TYPES
                    enemy_types = ENEMY_TYPES.get(element, ["Monster"])
                    next_enemy_type = random.choice(enemy_types)
                elif next_type == "miniboss":
                    next_enemy_type = f"{miniboss_element.value} Champion"
                elif next_type == "boss":
                    from envs.cuterpg.RoguelikeRPG.constants import BOSS_NAMES
                    next_enemy_type = BOSS_NAMES.get(boss_element, f"Ancient {boss_element.value} Destroyer")
                else:
                    next_enemy_type = None
            
            # Create the appropriate level type
            if level_type == "growth":
                level = GrowthLevel(level_number, 
                                    next_enemy_hint=next_enemy_type,
                                    reversible=self.reversible)
            elif level_type == "combat":
                # Choose a random element for the enemy
                other_elems = [e for e in all_elements if e != boss_element]
                # enemy_elements = random.choice(other_elems, self.single_level_enemy)
                enemy_elements = random.choices(other_elems, k=self.single_level_enemy)
                level = CombatLevel(level_number, 
                                    difficulty=1, 
                                    enemy_elements=enemy_elements,
                                    enemy_num = self.single_level_enemy,
                                    reversible=self.reversible)
            elif level_type == "miniboss":
                level = BossLevel(level_number, 
                                  is_final_boss=False, 
                                  boss_element=miniboss_element,
                                  reversible=self.reversible)
            elif level_type == "shop":
                level = ShopLevel(level_number, 
                                  next_enemy_hint=next_enemy_type,
                                  reversible=self.reversible)
            # elif level_type == "crafting":
            #     level = CraftingLevel(level_number, next_enemy_hint=next_enemy_type)
            elif level_type == "boss":
                level = BossLevel(level_number, 
                                  is_final_boss=True, 
                                  boss_element=boss_element,
                                  reversible=False) # we can never go back after we get to the boss level
            else:
                # Default to a growth level if the type is unknown
                level = GrowthLevel(level_number,
                                    reversible=self.reversible)
            
            self.levels.append(level)
        
        # Now that all levels are created, use the solution manager to ensure the game is solvable
        # print(self.levels)
        solution_manager = SolutionManager(self.levels, boss_element, self.player.inventory)
        self.solution_element = solution_manager.distribute_required_items()
        
        # Add hints about the boss's weaknesses
        solution_manager.add_hints_about_boss(len(self.levels) - 1)
        self.solution_manager = solution_manager
        # print("Random check:", random.random(), np.random.rand())
        return
    
    def start(self) -> str:
        """
        Start the game and enter the first level.
        
        Returns:
            str: Initial game state description
        """
        # Make sure we're at the beginning
        self.current_level_index = 0
        self.game_completed = False
        self.game_over = False
        
        # Get the first level
        current_level = self.get_current_level()
        
        # Enter the first level
        level_description = current_level.enter(self.player)
        self.level_descripion = level_description
        
        # Create the opening message
        mode_name = "Easy Mode" if self.mode == GameMode.EASY else "Hard Mode"
        opening = f"Welcome to RougelikeRPG ({mode_name})!\n\n"
        inventory = f"Your starting inventory:\n{self.player.inventory}\n\n"
        self.opening = opening
        
        return f"{opening}{inventory}You are now entering Level 1: {current_level.level_type.capitalize()}\n\n{level_description}"

    
    def get_current_level(self) -> Level:
        """
        Get the current level object.
        
        Returns:
            Level: The current level
        """
        return self.levels[self.current_level_index]
    
    def process_action(self, action: str, *args) -> Dict[str, Any]:
        """
        Process a player action.
        
        Args:
            action: The action to take
            args: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: Result of the action
        """
        # Check if the game is over
        if self.game_over:
            return {"success": False, "message": "Game over! You have been defeated."}
        
        if self.game_completed:
            return {"success": False, "message": "Congratulations! You have completed the game."}
        
        # Get the current level
        current_level = self.get_current_level()
        
        # Process the action in the current level
        result = current_level.process_action(self.player, action, *args)
        
        # Check if the player is still alive
        if not self.player.is_alive:
            self.game_over = True
            result["game_over"] = True
            result["message"] += "\n\nYou have been defeated! Game over."
            return result
        
        # Check if the level has been completed
        if current_level.back:
            self.get_current_level().completed = False
            self.get_current_level().back = False
            self.current_level_index -= 1
            next_level = self.get_current_level()
            next_level.completed = False
            next_level.back = False
            next_level_description = next_level.enter(self.player)
            self.level_descripion = next_level_description

            # result["next_level"] = True 
            result["next_level_number"] = next_level.level_number
            result["next_level_type"] = next_level.level_type
            result["next_level_description"] = next_level_description
            result["message"] += f"\n\nYou are now back to Level {next_level.level_number}: {next_level.level_type.capitalize()}.\n\n{next_level_description}"

        elif current_level.completed:
            # Move to the next level if available
            if self.current_level_index < len(self.levels) - 1:
                self.current_level_index += 1
                next_level = self.get_current_level()
                
                # Enter the next level
                next_level_description = next_level.enter(self.player)
                self.level_descripion = next_level_description
                
                result["next_level"] = True
                result["next_level_number"] = next_level.level_number
                result["next_level_type"] = next_level.level_type
                result["next_level_description"] = next_level_description
                result["message"] += f"\n\nYou proceed to Level {next_level.level_number}: {next_level.level_type.capitalize()}.\n\n{next_level_description}"
            else:
                # Game completed!
                self.game_completed = True
                result["game_completed"] = True
                result["message"] += "\n\nCongratulations! You have completed the game and proven yourself a worthy adventurer!"
        
        return result
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get the current state of the game.
        
        Returns:
            Dict[str, Any]: Current game state
        """
        current_level = self.get_current_level()
        
        state = {
            "game_mode": self.mode.name,
            "current_level_number": current_level.level_number,
            "current_level_type": current_level.level_type,
            "levels_completed": self.current_level_index,
            "total_levels": len(self.levels),
            "player_hp": f"{self.player.current_hp}/{self.player.max_hp}",
            "player_inventory": str(self.player.inventory),
            "equipped_weapon": str(self.player.equipped_weapon) if self.player.equipped_weapon else "None",
            "game_completed": self.game_completed,
            "game_over": self.game_over,
            "available_actions": current_level.available_actions
        }
        
        return state
    
    def verify_solvability(self) -> Dict[str, Any]:
        """
        Verify that this game is solvable.
        
        Returns:
            Dict[str, Any]: Verification results
        """
        from envs.cuterpg.RoguelikeRPG.utils.game_verification import EnhancedGameVerification
        return EnhancedGameVerification.verify_game_solvability(self)
    

    def reset_player_hp(self):
        weapons = self.solution_manager.expected_weapons
        #print(weapons)
        total_hp = 0
        for idx, level in enumerate(self.levels):
            if level.level_type == 'combat':
                hp_drops = []
                for enemy in level.enemies:
                   turns, total_damage_taken = enemy.simulate_battle(weapons[idx])
                   hp_drops.append(total_damage_taken)
                if self.shuffle_enemy:
                    total_hp += max(hp_drops)
                else:
                    total_hp += sum(hp_drops)
            elif level.level_type == 'boss':
                turns, total_damage_taken = level.enemy.simulate_battle(weapons[idx])
                total_hp += total_damage_taken

        self.player.max_hp = total_hp + 1
        self.player.current_hp = self.player.max_hp
        return
    
    def run_interactive(self):
        """
        Run the game in interactive mode, accepting commands from stdin.
        """
        # print(self.start())
        
        while not self.game_completed and not self.game_over:
            # Display the current level and available actions
            current_level = self.get_current_level()
            print(f"\nCurrent Level: {current_level.level_number} ({current_level.level_type.capitalize()})")
            print(f"Available actions: {', '.join(current_level.available_actions)}")
            print(f"HP: {self.player.current_hp}/{self.player.max_hp} | Equipped: {self.player.equipped_weapon if self.player.equipped_weapon else 'Nothing'}")
            
            # Show available interaction objects in the current level
            if hasattr(current_level, 'interactions') and current_level.interactions:
                print("\nThings you can interact with:")
                for obj_name, obj_info in current_level.interactions.items():
                    if "description" in obj_info:
                        print(f"- {obj_name}: {obj_info['description']}")
                    else:
                        print(f"- {obj_name}")
            
            # In combat levels, show enemy information
            if current_level.level_type in ["combat", "boss"] and hasattr(current_level, 'enemy') and current_level.enemy:
                print(f"\nEnemy: {current_level.enemy}")
            
            # Get player input
            try:
                command = input("\nWhat would you like to do? ").strip()
                
                # Exit the game if requested
                if command.lower() in ["exit", "quit"]:
                    print("Thanks for playing RougelikeRPG!")
                    break
                
                # Special handling for common command patterns
                # First try to split by space to get action
                parts = command.split(' ', 1)
                action = parts[0].lower()
                
                # Handle the argument part - we need to be flexible with how people input item names
                args = []
                if len(parts) > 1:
                    arg_text = parts[1].strip()
                    
                    # Remove brackets if they're present
                    if (arg_text.startswith('[') and arg_text.endswith(']')):
                        arg_text = arg_text[1:-1].strip()
                    
                    args = [arg_text]
                
                # Process the action
                result = self.process_action(action, *args)
                
                # Display the result
                print(f"\n{result['message']}")
                
                # Display additional content if available
                if "content" in result:
                    print(f"\n{result['content']}")
                
                # Check if the game has ended
                if self.game_completed or self.game_over:
                    break
                
            except EOFError:
                print("\nGame terminated by user.")
                break
            except KeyboardInterrupt:
                print("\nGame terminated by user.")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
        
        # Game end message
        if self.game_completed:
            print("\nCongratulations! You have completed the game!")
        elif self.game_over:
            print("\nGame over! You have been defeated.")