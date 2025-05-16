from .navigation import nav_react, nav_react_tiles, nav_react_obs, nav_tiles_obs, nav_react_turns, nav_turns_obs, nav_instruction_summer, nav_instruction_winter, nav_reflexion, nav_reflexion_guide, nav_subgoal, nav_plan_instruction_summer, nav_plan_instruction_winter
from .navigation_imperfect import nav_season, wrong_turn_obs, wrong_tile_obs, nav_construction_obs, nav_construction_tiles
from .cooking import cook_instruction, cook_react, cook_react_perfect, cook_react_descriptive, cook_react_multiserve, cook_reflexion_guide, cook_subgoal, cook_plan_instruction, cook_react_none
from .cooking_imperfect import cook_react_slightly_mismatched_recipe, cook_react_crop_gone, cook_react_storage_loss, cook_react_rookie_chef
from .roguelike import game_instruction, game_react, game_react_type3,game_react_type2,game_react_type1,game_instruction_back, game_react_type0, rogue_reflexion, rogue_reflexion_guide, rogue_plan_instruction, rogue_subgoal
from pdb import set_trace as st

PROMPTS = {'navigation':{},
           'cooking': {},
           'roguelike': {},
           }

PROMPTS['navigation']['instruction'] = {'summer': nav_instruction_summer,
                                        'winter': nav_instruction_winter,
                                        'summer_plan': nav_plan_instruction_summer,
                                        'winter_plan': nav_plan_instruction_winter}
PROMPTS['navigation']['react'] = {'encoded': nav_react}
PROMPTS['navigation']['react_perfect'] = {  'encoded_turns': nav_react_turns,
                                            'encoded_tiles': nav_react_tiles,
                                            'encoded_descriptive': nav_react_obs,
                                            'encoded_turns_obs': nav_turns_obs,
                                            'encoded_tiles_obs': nav_tiles_obs,
                                          }
PROMPTS['navigation']['react_imperfect'] = {  'seasonal_descriptive': nav_season,
                                              'wrong_turn_obs': wrong_turn_obs,
                                              'wrong_tile_obs': wrong_tile_obs,
                                              'nav_construction_obs': nav_construction_obs,
                                              'nav_construction_tiles': nav_construction_tiles,
                                            }
PROMPTS['navigation']['hierachical'] = {'follow': nav_subgoal}
PROMPTS['navigation']['reflexion'] = {'': nav_reflexion,
                                      'guide': nav_reflexion_guide}

PROMPTS['cooking']['instruction'] = {'encoded': cook_instruction,
                                     'plan': cook_plan_instruction}
PROMPTS['cooking']['react'] = {'encoded': cook_react}
PROMPTS['cooking']['react_none'] = {'encoded': cook_react_none}
PROMPTS['cooking']['react_perfect'] = {'encoded': cook_react_perfect}
PROMPTS['cooking']['react_descriptive'] = {'encoded': cook_react_descriptive,
                                           'multiserve': cook_react_multiserve,
                                           }
PROMPTS['cooking']['react_imperfect'] = {'slightly_mismatched_recipe': cook_react_slightly_mismatched_recipe,
                                         'crop-gone': cook_react_crop_gone,
                                         'storage-loss': cook_react_storage_loss,
                                         'rookie-chef': cook_react_rookie_chef,
                                         }

PROMPTS['cooking']['reflexion'] = {'': None,
                                      'guide': cook_reflexion_guide}
PROMPTS['cooking']['hierachical'] = {'follow': cook_subgoal}

PROMPTS['roguelike']['instruction'] = {'base': game_instruction,
                                       'reversible': game_instruction_back,
                                       'plan': rogue_plan_instruction}
PROMPTS['roguelike']['react'] = {'encoded': game_react}
PROMPTS['roguelike']['react_detailed'] = {'encoded':game_react_type3}
PROMPTS['roguelike']['react_list'] = {'encoded':game_react_type2}
PROMPTS['roguelike']['react_vague'] = {'encoded':game_react_type1}
PROMPTS['roguelike']['react_checkpoint'] = {'encoded':game_react_type0}
PROMPTS['roguelike']['reflexion'] = {'': rogue_reflexion,
                                      'guide': rogue_reflexion_guide}

PROMPTS['roguelike']['hierachical'] = {'follow': rogue_subgoal}

def get_prompt(type, env, args):
    if args.env_type == 'navigation':
        if type == 'instruction':
            if 'Seasonal' in args.env:
                if args.hierachical:
                    return PROMPTS[args.env_type][type]['winter_plan']
                else:
                    return PROMPTS[args.env_type][type]['winter']
            else:
                if args.hierachical:
                    return PROMPTS[args.env_type][type]['summer_plan']
                else:
                    return PROMPTS[args.env_type][type]['summer']
        elif type == 'reflexion':
            if args.manual_type is None:
                return PROMPTS['navigation']['reflexion']['']
            else:
                return PROMPTS['navigation']['reflexion']['guide']
        elif args.hierachical:
            return PROMPTS['navigation']['hierachical']['follow']

        if args.manual_type is None:
            few_shot_type = 'react'
            prompt_type = 'encoded'
        if args.manual_type == 0:
            # imperfect is for environment change, not manual imperfection
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_turns'
            # prompt_type = 'imperfect_general' if args.imperfect_aware == 'general' else 'encoded'
            if args.imperfect_aware == 'specific':
                if 'Construction' in args.env:
                    prompt_type = 'imperfect_construction'
                else:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'wrong_turn_obs'
        if args.manual_type == 1: 
            # imperfect is for environment change, not manual imperfection
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_tiles'
            # prompt_type = 'imperfect_general' if args.imperfect_aware == 'general' else 'encoded'
            if args.imperfect_aware == 'specific':
                if 'Construction' in args.env:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'nav_construction_tiles'
                else:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'wrong_tile_obs'
                    
        elif args.manual_type == 2:
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_descriptive'
            if args.imperfect_aware == 'specific':
                if 'Seasonal' in args.env:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'seasonal_descriptive'
                elif 'Construction' in args.env:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'nav_construction_obs'
                else:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'seasonal_descriptive'
                    
        elif args.manual_type == 3:
            # wrong number of turns, but has obs as indicator
            if not args.imperfect_aware:
                few_shot_type = 'react_perfect'
                prompt_type = 'encoded_turns_obs'
            elif args.imperfect_aware == 'specific':
                few_shot_type = 'react_imperfect'
                prompt_type = 'wrong_turn_obs'
                
        elif args.manual_type == 4:
            if not args.imperfect_aware:
                few_shot_type = 'react_perfect'
                prompt_type = 'encoded_tiles_obs'
            elif args.imperfect_aware == 'specific':
                few_shot_type = 'react_imperfect'
                prompt_type = 'wrong_tile_obs'

    elif args.env_type == 'cooking':
        if type == 'instruction':
            if args.hierachical:
                return PROMPTS[args.env_type][type]['plan']
            else:
                return PROMPTS[args.env_type][type]['encoded']
        elif type == 'reflexion':
            if args.manual_type is None:
                return PROMPTS['cooking']['reflexion']['']
            else:
                return PROMPTS['cooking']['reflexion']['guide']
        elif args.hierachical:
            return PROMPTS['cooking']['hierachical']['follow']
        
        if 'crop-gone' in args.env:
            if args.imperfect_aware:
                few_shot_type = 'react_imperfect'
                prompt_type = 'crop-gone'
            else:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
        elif 'storage-loss' in args.env:
            if args.imperfect_aware:
                few_shot_type = 'react_imperfect'
                prompt_type = 'storage-loss'
            else:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
        elif 'rookie-chef' in args.env:
            if args.imperfect_aware:
                few_shot_type = 'react_imperfect'
                prompt_type = 'rookie-chef'
            else:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
        elif 'multiserve' in args.env:
            if args.imperfect_aware:
                few_shot_type = 'react_descriptive'
                prompt_type = 'multiserve'
            else:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
        else:
            if args.manual_type is None:
                few_shot_type = 'react_none'
                prompt_type = 'encoded'
            if args.manual_type == 0:
                few_shot_type = 'react'
                prompt_type = 'encoded'
            if args.manual_type == 1:
                few_shot_type = 'react_perfect'
                prompt_type = 'encoded'
            elif args.manual_type == 2:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
                if args.imperfect_aware:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'storage-loss'
            elif args.manual_type == 4:
                if args.imperfect_aware:
                    few_shot_type = 'react_imperfect'
                    prompt_type = 'slightly_mismatched_recipe'
                else:
                    few_shot_type = 'react_descriptive'
                    prompt_type = 'encoded'

    elif args.env_type == 'roguelike':
        if type == 'instruction':
            if args.back:
                return PROMPTS[args.env_type]['instruction']['reversible']
            elif args.hierachical:
                return PROMPTS[args.env_type]['instruction']['plan']
            else:
                return PROMPTS[args.env_type]['instruction']['base']
        elif type == 'reflexion':
            if args.manual_type is None:
                return PROMPTS[args.env_type]['reflexion']['']
            else:
                return PROMPTS[args.env_type]['reflexion']['guide']
        elif args.hierachical:
            return PROMPTS[args.env_type]['hierachical']['follow']
        else:
            if args.manual_type is None:
                few_shot_type = 'react'
                prompt_type = 'encoded'
            elif args.manual_type == 0:
                few_shot_type = 'react_checkpoint'
                prompt_type = 'encoded'
            elif args.manual_type == 1:
                few_shot_type = 'react_vague'
                prompt_type = 'encoded'
            elif args.manual_type == 2:
                few_shot_type = 'react_list'
                prompt_type = 'encoded'
            elif args.manual_type >= 3:
                few_shot_type = 'react_detailed'
                prompt_type = 'encoded'
                if args.imperfect_aware:
                    raise AssertionError("Unexpected use of --imperfect_aware")
            elif args.manual_type == None:
                return ''
      

    return PROMPTS[args.env_type][few_shot_type][prompt_type]
