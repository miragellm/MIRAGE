import random
from collections import defaultdict
from envs.cuterpg.RoguelikeRPG.constants import STANDARD_WEAPONS, ADVANCED_WEAPONS, CRAFTING_RECIPES
from pdb import set_trace as st

def expand_crafting_tree(target_item: str):
    """
    Expand only the base materials (non-craftable) needed to craft a target item.

    Args:
        target_item (str): Final item to be crafted
        recipes (dict): Crafting recipe dictionary

    Returns:
        Dict[str, int]: Base material name -> required count
    """
    required = defaultdict(int)

    def recurse(item_name: str, multiplier: int):
        if item_name in CRAFTING_RECIPES:
            for sub_item, qty in CRAFTING_RECIPES[item_name]:
                recurse(sub_item, qty * multiplier)
        else:
            required[item_name] += multiplier

    recurse(target_item, 1)
    return dict(required)



def derangement(original_list):
    while True:
        shuffled = original_list[:]
        random.shuffle(shuffled)
        if all(o != s for o, s in zip(original_list, shuffled)):
            return shuffled