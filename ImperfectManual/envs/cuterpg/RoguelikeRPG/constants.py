"""
Constants and configurations for the RougelikeRPG game.
"""
import random
from enum import Enum, auto

# Game modes
class GameMode(Enum):
    EASY = auto()  # 6 layers
    HARD = auto()  # 8 layers

class Element(Enum):
    FIRE = "FIRE"
    WATER = "WATER"
    NATURE = "NATURE"
    LIGHT = "LIGHT"
    DARK = "DARK"
    ELECTRIC = "ELECTRIC"
    ICE = "ICE"
    EARTH = "EARTH"
    
    @classmethod
    def random(cls):
        """Returns a random element"""
        return random.choice(list(cls))

# Element effectiveness chart (attacker → defender)
# 2.0: Super effective, 1.0: Normal, 0.5: Not very effective, 0.0: Immune
ELEMENT_EFFECTIVENESS = {
    Element.FIRE: {
        Element.FIRE: 0.5,
        Element.WATER: 0.5,
        Element.NATURE: 2.0,
        Element.ICE: 2.0,
        Element.EARTH: 0.5,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.WATER: {
        Element.FIRE: 2.0,
        Element.WATER: 0.5,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 0.5,
    },
    Element.NATURE: {
        Element.FIRE: 0.5,
        Element.WATER: 2.0,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.ICE: {
        Element.FIRE: 0.5,
        Element.WATER: 0.5,
        Element.NATURE: 2.0,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.EARTH: {
        Element.FIRE: 2.0,
        Element.WATER: 0.5,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 1.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 2.0,
    },
    Element.LIGHT: {
        Element.FIRE: 1.0,
        Element.WATER: 1.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 1.0,
        Element.LIGHT: 0.5,
        Element.DARK: 2.0,
        Element.ELECTRIC: 1.0,
    },
    Element.DARK: {
        Element.FIRE: 1.0,
        Element.WATER: 1.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 1.0,
        Element.LIGHT: 2.0,
        Element.DARK: 0.5,
        Element.ELECTRIC: 1.0,
    },
    Element.ELECTRIC: {
        Element.FIRE: 1.0,
        Element.WATER: 2.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 0.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 0.5,
    },
}

# Item tiers and weights
class ItemTier(Enum):
    BASIC = 1     # Basic materials (weight 2)
    STANDARD = 2  # Standard weapons (weight 3)
    ADVANCED = 3  # Advanced weapons (weight 5)

# Item weights by tier
ITEM_WEIGHTS = {
    ItemTier.BASIC: 2,
    ItemTier.STANDARD: 3,
    ItemTier.ADVANCED: 5,
}

# Base materials (Tier 1)
BASE_MATERIALS = {
    "Fire Essence": Element.FIRE,
    "Water Crystal": Element.WATER,
    "Leaf Fragment": Element.NATURE,
    "Light Shard": Element.LIGHT,
    "Shadow Dust": Element.DARK,
    "Lightning Spark": Element.ELECTRIC,
    "Frost Particle": Element.ICE,
    "Earth Stone": Element.EARTH,
    "Weapon Prototype": None,  # Universal crafting material
    "Magic Catalyst": None,    # Universal crafting material
    "Enchanted Cloth": None,   # Universal crafting material
}

    
RENAME_MAP = {
    "Fire Essence": [
        "Burning Soul",      
        "Essence of Fire",  
        "Fire Fragment",    
        "Fire Residue",    
        "Flame Core"      
    ],
    "Water Crystal": [
        "Ocean Tear",      
        "Aqua Crystal",   
        "Water Gem",        
        "Crystal of Water",  
        "Mist Shard"        
    ],
    "Leaf Fragment": [
        "Leaf Shard",        
        "Verdant Fragment",   
        "Nature Chip",     
        "Forest Sliver",     
        "Herbal Splinter"     
    ],
    "Light Shard": ["Sunbeam Fragment", "Lightcore", "Radiant Chip"],
    "Shadow Dust": ["Whispering Ash", "Dark Residue", "Shadow Powder"],
    "Lightning Spark": ["Storm Seed", "Thunder Core", "Spark Fragment"],
    "Frost Particle": ["Frozen Whistle", "Ice Fragment", "Frostbite Chip"],
    "Earth Stone": ["Rooted Core", "Earthen Shard", "Dusty Rock"],
    "Weapon Prototype": ["Blank Weapon Core"],
    # "Magic Catalyst": ["Arcanite Core", "Spell Focus", "Mystic Orb"],
    "Enchanted Cloth": ["Mystic Wrap", "Woven Rune", "Arcane Fabric"]
}

# Standard weapons (Tier 2)
STANDARD_WEAPONS = {
    "Fire Staff": Element.FIRE,
    "Water Wand": Element.WATER,
    "Nature Bow": Element.NATURE,
    "Light Mace": Element.LIGHT,
    "Dark Dagger": Element.DARK,
    "Lightning Rod": Element.ELECTRIC,
    "Ice Sword": Element.ICE,
    "Earth Hammer": Element.EARTH,
}

# Advanced weapons (Tier 3)
ADVANCED_WEAPONS = {
    "Inferno Blaster": Element.FIRE,
    "Tsunami Trident": Element.WATER,
    "Gaia's Vengeance": Element.NATURE,
    "Divine Scepter": Element.LIGHT,
    "Void Reaper": Element.DARK,
    "Storm Caller": Element.ELECTRIC,
    "Glacier Blade": Element.ICE,
    "Mountain Breaker": Element.EARTH,
}

# Resulting mapping: item name -> weight
ITEM_WEIGHT_MAP = {}

# Add base materials (tier: BASIC)
for name in BASE_MATERIALS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.BASIC]

# Add standard weapons (tier: STANDARD)
for name in STANDARD_WEAPONS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.STANDARD]

# Add advanced weapons (tier: ADVANCED)
for name in ADVANCED_WEAPONS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.ADVANCED]
    
# Final mapping: item name -> type, tier, element
ITEM_INFO_MAP = {}

# Base materials (tier: BASIC)
for name, element in BASE_MATERIALS.items():
    ITEM_INFO_MAP[name] = {
        "type": "material",
        "tier": ItemTier.BASIC,
        "element": element
    }

# Standard weapons (tier: STANDARD)
for name, element in STANDARD_WEAPONS.items():
    ITEM_INFO_MAP[name] = {
        "type": "weapon",
        "tier": ItemTier.STANDARD,
        "element": element
    }

# Advanced weapons (tier: ADVANCED)
for name, element in ADVANCED_WEAPONS.items():
    ITEM_INFO_MAP[name] = {
        "type": "weapon",
        "tier": ItemTier.ADVANCED,
        "element": element
    }
    
# Crafting recipes
CRAFTING_RECIPES = {
    # Tier 2 weapons (Element + Prototype)
    "Fire Staff": [("Fire Essence", 1), ("Weapon Prototype", 1)],
    "Water Wand": [("Water Crystal", 1), ("Weapon Prototype", 1)],
    "Nature Bow": [("Leaf Fragment", 1), ("Weapon Prototype", 1)],
    "Light Mace": [("Light Shard", 1), ("Weapon Prototype", 1)],
    "Dark Dagger": [("Shadow Dust", 1), ("Weapon Prototype", 1)],
    "Lightning Rod": [("Lightning Spark", 1), ("Weapon Prototype", 1)],
    "Ice Sword": [("Frost Particle", 1), ("Weapon Prototype", 1)],
    "Earth Hammer": [("Earth Stone", 1), ("Weapon Prototype", 1)],
    
    # Element enhancers
    "Fire Enhancer": [("Fire Essence", 2), ("Magic Catalyst", 1)],
    "Water Enhancer": [("Water Crystal", 2), ("Magic Catalyst", 1)],
    "Nature Enhancer": [("Leaf Fragment", 2), ("Magic Catalyst", 1)],
    "Light Enhancer": [("Light Shard", 2), ("Magic Catalyst", 1)],
    "Dark Enhancer": [("Shadow Dust", 2), ("Magic Catalyst", 1)],
    "Lightning Enhancer": [("Lightning Spark", 2), ("Magic Catalyst", 1)],
    "Ice Enhancer": [("Frost Particle", 2), ("Magic Catalyst", 1)],
    "Earth Enhancer": [("Earth Stone", 2), ("Magic Catalyst", 1)],
    
    # Tier 3 weapons (Tier 2 weapon + Element enhancer)
    "Inferno Blaster": [("Fire Staff", 1), ("Fire Enhancer", 1), ("Enchanted Cloth", 1)],
    "Tsunami Trident": [("Water Wand", 1), ("Water Enhancer", 1), ("Enchanted Cloth", 1)],
    "Gaia's Vengeance": [("Nature Bow", 1), ("Nature Enhancer", 1), ("Enchanted Cloth", 1)],
    "Divine Scepter": [("Light Mace", 1), ("Light Enhancer", 1), ("Enchanted Cloth", 1)],
    "Void Reaper": [("Dark Dagger", 1), ("Dark Enhancer", 1), ("Enchanted Cloth", 1)],
    "Storm Caller": [("Lightning Rod", 1), ("Lightning Enhancer", 1), ("Enchanted Cloth", 1)],
    "Glacier Blade": [("Ice Sword", 1), ("Ice Enhancer", 1), ("Enchanted Cloth", 1)],
    "Mountain Breaker": [("Earth Hammer", 1), ("Earth Enhancer", 1), ("Enchanted Cloth", 1)],
}

# Enemy configurations
ENEMY_PREFIXES = [
    "Fierce", "Menacing", "Corrupted", "Ancient", "Mystic",
    "Furious", "Vigilant", "Restless", "Tranquil", "Rampaging"
]

ENEMY_TYPES = {
    Element.FIRE: ["Fire Imp", "Magma Golem", "Flame Sprite"],
    Element.WATER: ["Water Elemental", "Tide Lurker", "Rain Phantom"],
    Element.NATURE: ["Forest Guardian", "Vine Strangler", "Leaf Sprite"],
    Element.LIGHT: ["Radiant Angel", "Dawn Spirit", "Light Wisp"],
    Element.DARK: ["Shadow Walker", "Void Fiend", "Night Stalker"],
    Element.ELECTRIC: ["Thunder Beast", "Spark Phantom", "Lightning Elemental"],
    Element.ICE: ["Frost Giant", "Ice Golem", "Blizzard Spirit"],
    Element.EARTH: ["Stone Sentinel", "Rock Beast", "Crystal Giant"],
}

# Boss configurations
BOSS_NAMES = {
    Element.FIRE: "Inferno Overlord",
    Element.WATER: "Abyssal Hydra",
    Element.NATURE: "Ancient World Tree",
    Element.LIGHT: "Radiance Seraph",
    Element.DARK: "Void Emperor",
    Element.ELECTRIC: "Thunderstorm Archon",
    Element.ICE: "Eternal Frost Titan",
    Element.EARTH: "Mountain Colossus",
}

# Game level configurations
EASY_MODE_LAYERS = ["growth", "growth", "combat", "growth", "shop", "boss"]
HARD_MODE_LAYERS = ["growth", "combat", "growth", "growth", "miniboss", "growth", "shop", "boss"]

# Inventory configurations
INITIAL_INVENTORY_CAPACITY = 12
CAPACITY_INCREASE_COMBAT = 2
CAPACITY_INCREASE_MINIBOSS = 3

# Combat configurations
ENEMY_BASE_HP_RANGE = (40, 60)
MINIBOSS_HP_RANGE = (80, 120)
BOSS_HP_RANGE = (150, 200)

ENEMY_DAMAGE_LOW = 6
ENEMY_DAMAGE_HIGH = 8