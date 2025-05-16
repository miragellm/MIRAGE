"""
Solution manager to ensure games are solvable with guaranteed paths to defeat bosses.
"""
import random
import copy
from collections import defaultdict
from typing import List
from envs.cuterpg.RoguelikeRPG.constants import Element, BASE_MATERIALS
from envs.cuterpg.RoguelikeRPG.entities.boss import Boss
from envs.cuterpg.RoguelikeRPG.entities.item import create_material
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.levels.growth_level import GrowthLevel
from envs.cuterpg.RoguelikeRPG.levels.combat_level import CombatLevel
from envs.cuterpg.RoguelikeRPG.levels.shop_level import ShopLevel
from envs.cuterpg.RoguelikeRPG.constants import ITEM_WEIGHT_MAP, ADVANCED_WEAPONS, CRAFTING_RECIPES
from ..systems.virtual_inventory import VirtualInventory
from pdb import set_trace as st

class SolutionManager:
    """
    Manages the solution path for the game, ensuring that players can
    obtain the necessary items to defeat bosses.
    """
    
    def __init__(self, 
                 levels: List[Level], 
                 boss_element: Element,
                 inventory):
        """
        Initialize the solution manager.
        
        Args:
            levels: The list of game levels
            boss_element: The primary element of the final boss
        """
        self.levels = levels
        self.boss_element = boss_element
        self.inventory = inventory
        self.solution_element = None
        self.required_items = {}
        self.shop_items = []
        
        # Determine the solution path
        self._determine_solution_path()
    
    def _determine_solution_path(self):
        """
        Determine an optimal solution path to defeat the boss.
        """
        # Get elements that are effective against the boss
        counter_elements = Boss.get_weakness_elements(self.boss_element)
        
        # Choose one counter element as the primary solution path
        if counter_elements:
            self.solution_element = random.choice(sorted(counter_elements, key=lambda e: e.name))
        else:
            # If no direct counters, choose a random element that isn't the boss element
            all_elements = [e for e in Element if e != self.boss_element]
            self.solution_element = random.choice(all_elements)
            
        # Determine the element material name for the solution element
        element_material_name = None
        for name, element in BASE_MATERIALS.items():
            if element == self.solution_element:
                element_material_name = name
                break
        
        if not element_material_name:
            # Fallback if element material not found
            element_material_name = f"{self.solution_element.name} Essence"

        self.expected_weapons = [[] for _ in range(len(self.levels))]
        self.expected_inv = [[] for _ in range(len(self.levels))]
        self.remaining_capcities = [0 for _ in range(len(self.levels))]

        self.recommended_weapon = self.get_recommended_weapon()

        # Define the required items for the solution
        self.required_items = {
            # Basic materials needed (3 of the solution element - 1 for weapon, 2 for enhancer)
            element_material_name: 3,
            "Weapon Prototype": 1,
            "Magic Catalyst": 1,
            "Enchanted Cloth": 1
        }

    def distribute_required_items(self):
        """
        Distribute required items into levels with inventory capacity constraint,
        allowing backtracking if no valid distribution is found.
        """
        print_info = True
        
        # Step 1: Start with a copy of required items
        needed_items = copy.deepcopy(self.required_items)
        virtual_inventory = VirtualInventory(capacity=self.inventory.capacity)

        # Step 2: Fill virtual_inventory with already existing items from inventory
        for item in self.inventory.items:
            if item.name in self.required_items:
                required_count = needed_items[item.name]
                add_count = min(item.count, required_count)
                
                # Add to virtual inventory
                virtual_inventory.add_item(create_material(item.name, "", count=add_count))
                
                # Decrease needed amount
                needed_items[item.name] -= add_count
                
                # If fully satisfied, remove from needed_items
                if needed_items[item.name] == 0:
                    del needed_items[item.name]
                    
        placed = defaultdict(list)
        remaining = copy.deepcopy(needed_items)
            
        def backtrack(level_idx, placed, inv, remaining):
            if all(v == 0 for v in remaining.values()):
                for future_idx in range(level_idx, len(self.levels)):
                    self.expected_weapons[future_idx] = inv.get_all_weapons()

                for future_idx in range(level_idx, len(self.levels)):
                    self.expected_inv[future_idx] = copy.deepcopy(inv.items)
                return True

            if level_idx >= len(self.levels):
                return False
            
            level = self.levels[level_idx]
            if level.level_type in ["growth", "combat", "shop"]:
                candidates = [item for item, count in remaining.items() if count > 0]
                random.shuffle(candidates)

                for item in candidates:
                    w = ITEM_WEIGHT_MAP[item]

                    if inv.can_add(w):
                        inv.add_item(create_material(item, ''))
                        inv.try_all_possible_crafts()
                        self.expected_weapons[level_idx] = inv.get_all_weapons()
                        self.remaining_capcities[level_idx] = inv.remaining_capacity
                        self.expected_inv[level_idx] = copy.deepcopy(inv.items)

                        placed[level].append(item)
                        remaining[item] -= 1

                        if backtrack(level_idx + 1, placed, inv, remaining):
                            return True
                        # backtrack
                        placed[level].pop()
                        remaining[item] += 1
                        inv.remove_item(item, 1)
                        inv.breakdown()
                        inv.try_all_possible_crafts()
                        self.expected_weapons[level_idx] = inv.get_all_weapons()
                        self.remaining_capcities[level_idx] = inv.remaining_capacity
                        self.expected_inv[level_idx] = copy.deepcopy(inv.items)

            # try skipping this level
            if backtrack(level_idx + 1, placed, inv, remaining):
                return True

            return False

        found = backtrack(0, placed, virtual_inventory, remaining)
        # self.expected_weapons[-1] = self.expected_weapons[-2]
        # however this is weapon after, not weapon before...
        # as we can't collect items in the combat level, we should consider something before this
        self.expected_weapons.insert(0, [])
        # self.expected_weapons = self.expected_weapons[:-1]
        self.remaining_capcities[-1] = self.remaining_capcities[-2]
        if not found:
            st()
        self.required_placed = placed

        # Step 4: Commit placement
        for level, items in placed.items():
            for item_name in items:
                if level.level_type == "growth":
                    self._add_item_to_growth_level(level, item_name)
                elif level.level_type == "combat":
                    self._add_item_to_combat_level(level, item_name)
                elif level.level_type == "shop":
                    self._add_item_to_shop_level(level, item_name)

        self.full_required_items = copy.deepcopy(needed_items)
        self._add_complementary_elements(print_info=print_info)

        if print_info:
            print("[Distribution] Final item (only required ones) placement:")
            for level, items in placed.items():
                print(f"  - Level {self.levels.index(level)+1} ({level.level_type}): {items}")


        return self.solution_element

    
    def _add_item_to_growth_level(self, level: GrowthLevel, item_name: str):
        """
        Add an item to a growth level.
        
        Args:
            level: The growth level to add the item to
            item_name: The name of the item to add
        """
        # Determine if it should be a collectible or in a container
        if random.random() < 0.6:
            # Add to collectibles
            if item_name in BASE_MATERIALS:
                element = BASE_MATERIALS[item_name]
                description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            else:
                description = "A universal crafting material used in many recipes."
            
            item = create_material(item_name, description)
            
            # Add to collectibles with a description
            level.collectibles[item_name] = {
                "description": f"You see a {item_name} on the ground that seems important.",
                "item": item
            }
            level.interactions[item_name] = level.collectibles[item_name]
        else:
            # Add to a container
            if item_name in BASE_MATERIALS:
                element = BASE_MATERIALS[item_name]
                description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            else:
                description = "A universal crafting material used in many recipes."
            
            item = create_material(item_name, description)
            
            # Create or select a container
            container_names = ["treasure chest", "wooden crate", "mysterious box", "ancient container"]
            container_name = random.choice(container_names)
            
            # Make sure the container doesn't already exist
            if container_name not in level.containers:
                level.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something useful.",
                    "opened": False,
                    "content_description": f"You found a {item_name} inside!",
                    "item": item
                }
                level.interactions[container_name] = level.containers[container_name]
            else:
                # If container exists, add directly to collectibles instead
                level.collectibles[item_name] = {
                    "description": f"You notice a {item_name} partially hidden in the environment.",
                    "item": item
                }
                level.interactions[item_name] = level.collectibles[item_name]
    
    def _add_item_to_combat_level(self, level: CombatLevel, item_name: str):
        """
        Add an item to a combat level's enemy drops.
        
        Args:
            level: The combat level to add the item to
            item_name: The name of the item to add
        """
        if not level.enemies:
            return
        
        # Create the item
        if item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        else:
            description = "A universal crafting material used in many recipes."
        
        item = create_material(item_name, description)
        
        # Add to enemy drops
        enemy = random.choice(level.enemies)
        enemy.drops.append(item)

    def find_valid_range_to_shop(self, 
                                 shop_idx=-2,
                                 min_capacity: int = 2):
        if len(self.remaining_capcities) < 2:
            return None

        abs_shop_idx = len(self.remaining_capcities) + shop_idx if shop_idx < 0 else shop_idx

        start_idx = abs_shop_idx
        while start_idx >= 0 and self.remaining_capcities[start_idx] >= min_capacity:
            start_idx -= 1

        # If we never found a valid entry
        if start_idx == abs_shop_idx:
            return None

        return (start_idx + 1, abs_shop_idx)
    
    def _add_item_to_shop_level(self, level: ShopLevel, item_name: str):
        # these only include the must-buys 
        """
        Add an item to a shop level's inventory.
        
        Args:
            level: The shop level to add the item to
            item_name: The name of the item to add
        """
        # Create the item
        if item_name in BASE_MATERIALS:
            element = BASE_MATERIALS[item_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        else:
            description = "A universal crafting material used in many recipes."
        
        item = create_material(item_name, description)
        
        # Set a reasonable price (trade requirements)
        # Make sure it's something different than the item itself
        
        if item_name in self.required_items:
            valid_range = self.find_valid_range_to_shop()
            if valid_range is None:
                price_item = 'coin'
                source_level = None  # No layer info
            else:
                all_items = []
                item_sources = []
                for idx, l in enumerate(self.levels[valid_range[0]:-2]):
                    level_index = valid_range[0] + idx
                    items = l.get_available_item_names()
                    items = [x for x in items if x not in self.required_items]
                    all_items.extend(items)
                    item_sources.extend([level_index] * len(items))
                
                chosen_index = random.randrange(len(all_items))
                price_item = all_items[chosen_index]
                source_level = self.levels[item_sources[chosen_index]]
                
                self.shop_items.append((price_item, source_level))

        else:
            all_materials = [name for name in BASE_MATERIALS.keys() if name != item_name]
            if not all_materials:  # Safety check
                all_materials = ["Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"]
            
            price_item = random.choice(all_materials)

        price = [(price_item, 1)]
        
        # Add to shop inventory
        level.for_sale[item_name] = {
            "item": item,
            "price": price,
            "description": f"A {item_name} that seems useful for crafting."
        }
    
    def _add_complementary_elements(self, print_info):
        """
        Add non-essential elements to increase variety and exploration options.
        """
        # all_elements = list(Element)
        # complementary_elements = [e for e in all_elements if e != self.solution_element]
        has_required = False
        materials_to_consider = {name: element for name, element in BASE_MATERIALS.items() if element is not None}
        
        for level in self.levels:
            # Skip final boss level for complementary elements
            if level == self.levels[-1]:
                continue
            
            # Add 1-2 complementary items to non-boss levels
            if level.level_type in ["growth", "combat", "shop"]:
                num_items = random.randint(1, 2)
                num_to_sample = 1
                if level.level_type == 'combat':
                    num_items = level.enemy_num
                for _ in range(num_items):
                    # Select random complementary element
                    if has_required:
                        sample_pool = {name: element for name, element in materials_to_consider.items() if name not in self.full_required_items}
                    else:
                        sample_pool = materials_to_consider

                    selected_items = random.sample(list(sample_pool.items()), k=num_to_sample)
                    for element_material_name, complementary_element in selected_items:
                        if element_material_name in self.full_required_items:
                            has_required = True
                        
                        # Add to level based on level type
                        if level.level_type == "growth":
                            self._add_complementary_to_growth(level, element_material_name, complementary_element)
                        elif level.level_type == "combat":
                            self._add_complementary_to_combat(level, element_material_name, complementary_element)
                        elif level.level_type == "shop":
                            self._add_complementary_to_shop(level, element_material_name, complementary_element)
                        
                        # Print info if needed
                        if print_info:
                            print(f"[Info] Added {element_material_name} ({complementary_element.name}) to {level.level_type} level.")
        
      
    def _add_complementary_to_growth(self, level: GrowthLevel, item_name: str, element: Element):
        """Add a complementary element item to a growth level."""
        # Check if the item already exists in the level
        if item_name in level.collectibles or any(c.get("item") and c.get("item").name == item_name for c in level.containers.values()):
            return
        
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Either add as collectible or in container
        if random.random() < 0.7:
            level.collectibles[item_name] = {
                "description": f"You see a {item_name} that might be useful.",
                "item": item
            }
            level.interactions[item_name] = level.collectibles[item_name]
        else:
            container_names = ["small pouch", "hidden cache", "natural formation", "abandoned pack"]
            container_name = random.choice(container_names)
            
            if container_name not in level.containers:
                level.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something.",
                    "opened": False,
                    "content_description": f"You found a {item_name} inside!",
                    "item": item
                }
                level.interactions[container_name] = level.containers[container_name]
    
    def _add_complementary_to_combat(self, level: CombatLevel, item_name: str, element: Element):
        """Add a complementary element item to a combat level's enemy drops."""
        if not level.enemies:
            return
            
        enemy = random.choice(level.enemies)
        # Check if the enemy already drops this item
        if any(drop.name == item_name for drop in enemy.drops if not isinstance(drop, str)):
            return
            
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Only add if the enemy doesn't already have too many drops
        if len(enemy.drops) < 3:
            enemy.drops.append(item)
    
    def _add_complementary_to_shop(self, level: ShopLevel, item_name: str, element: Element):
        """Add a complementary element item to a shop level's inventory."""
        # Check if the item is already in the shop
        if item_name in level.for_sale:
            return
            
        description = f"A basic crafting material with {element.value} elemental properties."
        item = create_material(item_name, description, element)
        
        # Set price
        all_materials = list(BASE_MATERIALS.keys())
        price_item = random.choice(all_materials)
        price = [(price_item, 1)]
        
        # Add to shop with a limited number of items
        if len(level.for_sale) < 6:
            level.for_sale[item_name] = {
                "item": item,
                "price": price,
                "description": f"A {item_name} with {element.value} properties."
            }

    def add_hints_about_boss(self, final_boss_level_index: int):
        """
        Add hints about the boss's weaknesses throughout the game.
        
        Args:
            final_boss_level_index: Index of the final boss level
        """
        # Create different types of hints
        hint_types = [
            f"The {self.boss_element.value} boss ahead is weak against {self.solution_element.value} attacks.",
            f"I've heard that {self.solution_element.value} weapons are effective against {self.boss_element.value} creatures.",
            f"To defeat a {self.boss_element.value} enemy, you'll want to use {self.solution_element.value} elemental weapons.",
            f"The ancient texts say that {self.boss_element.value} beings fear the power of {self.solution_element.value}."
        ]
        
        # Add hints to NPCs and readable objects in growth levels
        growth_levels = [level for level in self.levels if level.level_type == "growth" 
                        and self.levels.index(level) < final_boss_level_index]
        
        if not growth_levels:
            return
            
        # Choose up to 2 growth levels to add hints
        hint_levels = random.sample(growth_levels, min(2, len(growth_levels)))
        
        for level in hint_levels:
            hint = random.choice(hint_types)
            
            # Add to an NPC if available
            if level.npcs:
                npc_name = random.choice(list(level.npcs.keys()))
                level.npcs[npc_name]["dialog"] = f"\"Listen carefully, adventurer. {hint}\""
            
            # Or add to a readable object
            elif level.readables:
                readable_name = random.choice(list(level.readables.keys()))
                level.readables[readable_name]["content"] = f"The writing reveals: \"{hint}\""
            
            # If no NPCs or readables, create a new readable
            else:
                readable_name = random.choice(["ancient scroll", "mysterious tablet", "traveler's note", "forgotten tome"])
                level.readables[readable_name] = {
                    "description": f"There's a {readable_name} here with some writing on it.",
                    "content": f"The writing reveals: \"{hint}\""
                }
                level.interactions[readable_name] = level.readables[readable_name]
        
        # Also add a hint to the shopkeeper if a shop level exists
        shop_levels = [level for level in self.levels if level.level_type == "shop" 
                      and self.levels.index(level) < final_boss_level_index]
                      
        if shop_levels:
            shop_level = shop_levels[0]
            hint = random.choice(hint_types)
            
            # Add the hint as a potential shopkeeper dialog
            shop_dialogs = [
                f"\"A word of advice before you go further. {hint}\"",
                f"\"For a seasoned adventurer like you, this might be useful to know: {hint}\"",
                f"\"Between you and me? {hint} That'll be free advice, no charge.\""
            ]
            
            shop_hint = random.choice(shop_dialogs)
            shop_level._talk_to_shopkeeper = lambda: {"success": True, "message": f"{shop_level.shopkeeper_name} says: {shop_hint}"}


    def get_recommended_weapon(self):
        chosen_weakness = self.solution_element
        # Find a weapon matching the weakness
        possible_weapons = []
        # we can only fight them with advanced weapons
        for weapon_name, element in ADVANCED_WEAPONS.items():
            if element == chosen_weakness:
                possible_weapons.append(weapon_name)

        if not possible_weapons:
            return f"Warning: No available weapons matching the weakness {chosen_weakness.name} were found."

        recommended_weapon = possible_weapons[-1]
        return recommended_weapon
            
    def get_solution_path(self, manual_type) -> str:
        """
        Return the full solution path: boss info, weakness, recommended weapon, and full crafting steps in natural English.
        
        Returns:
            str
        """
        if not self.solution_element:
            raise ValueError("Solution path not initialized. Call distribute_required_items() first.")

        boss_element = self.boss_element
        chosen_weakness = self.solution_element
        recommended_weapon = self.recommended_weapon

        # Recursively expand crafting steps
        crafting_steps = self.expand_crafting_chain(recommended_weapon, manual_type)

        # Build the natural language description
        lines = []
        lines.append(f"You will face a {boss_element.name}-element boss on the final floor.")
        
        if manual_type is None:
            return "\n".join(lines)

        if manual_type is not None:
            lines.append(f"To counter it effectively, we recommend using a {chosen_weakness.name}-element weapon: {recommended_weapon}.")
            lines.append("")
            lines.append(f"To craft {recommended_weapon}, follow these steps:")

            for step in crafting_steps:
                lines.append(f"- {step}")

        lines.append("")
        
        if manual_type == 0:
            lines.append("Make sure that you have the following items in your inventory when you leave each of the levels:")

            # shop_item_map: level_id -> [item_name, ...]
            shop_item_map = defaultdict(list)
            for item_name, level in self.shop_items:
                for level_id in range(level.level_number-1, len(self.levels)-2):
                    shop_item_map[level_id].append(item_name)

            for level_id, items in enumerate(self.expected_inv[:-1]):
                lines.append(f"  Level {self.levels[level_id].level_number} ({self.levels[level_id].level_type}):")

                # add expected inventory items
                for item in items:
                    lines.append(f"    - {item.name} ×{item.count}")

                for item_name in shop_item_map.get(level_id, []):
                    lines.append(f"    - {item_name} ×1")

            lines.append("")
            lines.append(f"To fight the enemies, make sure to:")
            for level_id_ori, level in enumerate(self.levels):
                level_id = level_id_ori + 1
                if level.level_type in ['combat', 'boss']:
                    if self.expected_weapons:
                        weapons = self.expected_weapons[level_id-1] #this is something you got from last level
                        if weapons:
                            if level.level_type == 'boss' or len(level.enemies) == 1:
                                lines.append(
                                    f"Level {self.levels[level_id_ori].level_number} ({level.level_type}): Arm yourself with the most powerful weapon against the enemies.")
                            else:
                                lines.append(
                                    f"Level {self.levels[level_id_ori].level_number} ({level.level_type}): Arm yourself with the most powerful weapon against the enemies. You should beat at least one of the enemies to be able to proceed."
                                )
                            all_enemies = level.enemies if level.level_type=='combat' else [level.enemy]

                            for enemy in all_enemies:
                                best_weapon = max(weapons, key=lambda w: enemy.get_weapon_damge(w))
                                damage = enemy.get_weapon_damge(best_weapon)
    
                                if damage < 5:
                                    weapon_name = "your bare hands"
                                else:
                                    weapon_name = best_weapon.name

                                lines.append(
                                    f" - To fight {enemy.name} ({enemy.element.value}), use {weapon_name}."
                                )
                    
        elif manual_type == 1:
            lines.append("You will need to prepare the following materials:")
            for material, qty in self.required_items.items():
                lines.append(f"- {material} ×{qty}")

            # the backtrack code ensures that only one required item in the store.
            for item, level in self.shop_items:
                lines.append(f"- {item} x 1")

            lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")

        elif manual_type == 2:
            lines.append("You will need to collect items from the following levels:")
            level_to_items = defaultdict(lambda: defaultdict(int))

            # required_placed
            for level in self.required_placed:
                for material in self.required_placed[level]:
                    level_to_items[level][material] += 1

            # shop_items (assume list of (item, level))
            for item, level in self.shop_items:
                level_to_items[level][item] += 1

            # print combined info
            for level, item_counts in level_to_items.items():
                header = f"Level {level.level_number} ({level.level_type}):"
                lines.append(header)
                for item, count in item_counts.items():
                    lines.append(f" - {item} ×{count}")

            lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")
                    
        elif manual_type in [3, 5]:
            lines.append("You will need to collect items from the following levels:")
            level_to_items = defaultdict(lambda: defaultdict(int))

            # required_placed
            for level in self.required_placed:
                for material in self.required_placed[level]:
                    level_to_items[level][material] += 1

            # shop_items (assume list of (item, level))
            for item, level in self.shop_items:
                level_to_items[level][item] += 1

            # print combined info
            for level, item_counts in level_to_items.items():
                header = f"Level {level.level_number} ({level.level_type}):"
                lines.append(header)

                for item, count in item_counts.items():
                    sources = self.get_item_sources(level, item)
                    if sources:
                        source_info = ', '.join(sources)
                        if len(sources) > count:
                            source_info += f'. you only need to collect {count} of them.'
                        lines.append(f" - {item} ×{count} ({source_info})")
                    else:
                        lines.append(f" - {item} ×{count}")

            lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")

        elif manual_type == 4:
            lines.append("Make sure to collect items when you are at these levels:")
            level_to_items = defaultdict(lambda: defaultdict(int))

            # required_placed
            for level in self.required_placed:
                for material in self.required_placed[level]:
                    level_to_items[level][material] += 1

            # shop_items (assume list of (item, level))
            for item, level in self.shop_items:
                level_to_items[level][item] += 1

            sampled_keys = set(random.sample(list(level_to_items.keys()), k=len(level_to_items) // 2))

            # Iterate over original dict, but only use the sampled keys
            for level, item_counts in level_to_items.items():
                if level in sampled_keys:
                    header = f"Level {level.level_number} ({level.level_type}):"
                    lines.append(header)

                    for item, count in item_counts.items():
                        sources = self.get_item_sources(level, item)
                        if sources:
                            source_info = ', '.join(sources)
                            if len(sources) > count:
                                source_info += f'. you only need to collect {count} of them.'
                            lines.append(f" - {item} ×{count} ({source_info})")
                        else:
                            lines.append(f" - {item} ×{count}")

            lines.append(f"Everytime you want to fight an enemy, arm yourself with the most powerful weapon against it.")
                        
        # self.print_layout()
        return "\n".join(lines)
    
    def get_item_sources(self, level, item_name: str) -> List[str]:
        sources = []

        # Check collectibles
        if hasattr(level, "collectibles"):
            for name, info in level.collectibles.items():
                if name == item_name:
                    sources.append("on the ground")

        # Check containers
        if hasattr(level, "containers"):
            for container_name, info in level.containers.items():
                if info.get("item") and info["item"].name == item_name:
                    sources.append(f"in the {container_name}")

        # Check enemy drops
        if hasattr(level, 'enemies') and level.enemies:
            for enemy in level.enemies:
                for drop in getattr(enemy, "drops", []):
                    if isinstance(drop, str):
                        if drop == item_name:
                            sources.append(f"from defeating {enemy.name}")
                    elif drop.name == item_name:
                        sources.append(f"from defeating {enemy.name}")

        # Check shop
        if hasattr(level, "for_sale") and item_name in level.for_sale:
            sources.append("in the shop")
            
        sources = [f'one {x}' for x in sources]
        return sources

    def expand_crafting_chain(self, item_name, manual_type, corruption_state=None):
        """
        Recursively expand the crafting steps needed to make item_name, 
        introducing at most 1-2 recipe errors across the entire chain if manual_type==5.

        Args:
            item_name (str): The item to craft.
            manual_type (int): Manual version (5 allows corruptions).
            corruption_state (dict): Tracks which items have been corrupted.

        Returns:
            List[str]: Step-by-step crafting instructions.
        """
        if corruption_state is None:
            corruption_state = {
                "corrupted_items": set(),
                "max_corruptions": 2,
                "remaining_corruptions": 2
            }

        steps = []
        recipe = CRAFTING_RECIPES.get(item_name)

        # First, expand children recursively
        for material, qty in recipe:
            if material in CRAFTING_RECIPES:
                steps += self.expand_crafting_chain(material, manual_type, corruption_state)

        # Decide whether to corrupt this recipe
        corrupt_this = False
        if manual_type == 5 and corruption_state["remaining_corruptions"] > 0:
            # Corrupt this step with probability:
            if len(recipe) > 1 or corruption_state["remaining_corruptions"] == corruption_state["max_corruptions"]:
                # Strong bias to ensure at least one is corrupted
                corrupt_this = True
                corruption_state["remaining_corruptions"] -= 1
                corruption_state["corrupted_items"].add(item_name)

        # Possibly corrupted recipe
        if corrupt_this:
            fake_recipe = recipe.copy()
            num_to_replace = 1
            if len(fake_recipe) > 1 and corruption_state["remaining_corruptions"] > 0 and random.random() < 0.1:
                num_to_replace = 2
                corruption_state["remaining_corruptions"] -= 1

            existing_materials = [mat for mat, _ in fake_recipe]
            replacement_candidates = [m for m in BASE_MATERIALS if m not in existing_materials]
            indices = random.sample(range(len(fake_recipe)), num_to_replace)

            for i in indices:
                if replacement_candidates:
                    fake_mat = random.choice(replacement_candidates)
                    fake_recipe[i] = (fake_mat, fake_recipe[i][1])

            recipe_for_display = fake_recipe
        else:
            recipe_for_display = recipe

        # material_list = ', '.join([f"{qty} {material}" for material, qty in recipe_for_display])
        material_list = ', '.join([pluralize(material, qty) for material, qty in recipe_for_display])
        steps.append(f"Craft {item_name} using {material_list}")

        return steps
    
    def print_layout(self):
        """
        Print the layout of all levels: type, and available items with sources.
        """
        print("\n=== GAME LEVEL LAYOUT ===\n")
        for idx, level in enumerate(self.levels):
            header = f"Level {idx + 1} ({level.level_type})"
            print(header)
            print("-" * len(header))

            found_any = False

            # 1. Ground items
            if hasattr(level, "collectibles") and level.collectibles:
                for item_name, info in level.collectibles.items():
                    if "item" in info:
                        print(f"- {item_name} (on the ground)")
                        found_any = True

            # 2. Containers
            if hasattr(level, "containers") and level.containers:
                for container_name, info in level.containers.items():
                    item = info.get("item")
                    if item:
                        print(f"- {item.name} (in the {container_name})")
                        found_any = True

            # 3. Enemy drops
            if hasattr(level, "enemies") and level.enemies:
                for enemy in level.enemies:
                    for drop in getattr(enemy, "drops", []):
                        if isinstance(drop, str):
                            print(f"- {drop} (from defeating {enemy.name})")
                        else:
                            print(f"- {drop.name} (from defeating {enemy.name})")
                        found_any = True

            # 4. Shop items
            if hasattr(level, "for_sale") and level.for_sale:
                for item_name in level.for_sale:
                    print(f"- {item_name} (in the shop)")
                    found_any = True

            if not found_any:
                print("  (No obtainable items found in this level.)")

            print("")  # Add blank line between levels



def pluralize(name: str, qty: int) -> str:
    return f"{qty} {name if qty == 1 else name + 's'}"