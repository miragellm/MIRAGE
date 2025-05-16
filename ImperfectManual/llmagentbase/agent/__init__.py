from .navigator import Navigator
from .navigate_planner import NavigatePlanner
from .chef import Chef
from .adventurer import Adventurer
from .cook_planner import CookPlanner
from .game_planner import GamePlanner
from pdb import set_trace as st


def build_agent(env,
                instruction,
                in_context,
                logger,
                train_temperature,
                args = None):
    if args.env_type == 'navigation':
        manual = args.manual_type
        if args.hierachical:
            agent = NavigatePlanner(env,
                                    instruction,
                                    in_context,
                                    logger,
                                    args.agent_model,
                                    train_temperature,
                                    manual)
        else:
            agent = Navigator(  env,
                                instruction,
                                in_context,
                                logger,
                                args.agent_model,
                                train_temperature,
                                manual)
            
    elif args.env_type == 'cooking':
        manual = args.manual_type
        if args.hierachical:
            agent = CookPlanner(  env,
                            instruction,
                            in_context,
                            logger,
                            args.agent_model,
                            train_temperature,
                            manual)
        else:
            agent = Chef(  env,
                                instruction,
                                in_context,
                                logger,
                                args.agent_model,
                                train_temperature,
                                manual)
    elif args.env_type == 'roguelike':
        manual = args.manual_type
        if args.hierachical:
            agent = GamePlanner(  env,
                                    instruction,
                                    in_context,
                                    logger,
                                    args.agent_model,
                                    train_temperature,
                                    manual)
        else:
            agent = Adventurer(  env,
                                    instruction,
                                    in_context,
                                    logger,
                                    args.agent_model,
                                    train_temperature,
                                    manual)
        
        
    return agent