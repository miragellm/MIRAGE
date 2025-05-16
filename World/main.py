import argparse
import yaml
import wandb
from common.utils import set_seed
from common.logger import Logger
from llmagentbase import meta_train, meta_test
from pdb import set_trace as st


def main(args, logger):
    # set seed
    set_seed(args.seed)
    if not args.debug:
        wandb.init(
            project="mirage3", 
            entity="lyneylynettemagic-university-of-michigan", 
            name=args.log_name,
            config={k: str(v) if v is None else v for k, v in vars(args).items()}
        )
    if args.train:
        # if you want to train something
        meta_train(args, logger)
    meta_test(args, logger)


if __name__ == "__main__":
    # initialize argparse
    parser = argparse.ArgumentParser(description="llmagentbase")
    parser.add_argument(
        "--seed", type=int, default=0,
        help="random seed"
    )
    parser.add_argument(
        "--train", action="store_true",
        help="if True, perform training first. "
    )
    parser.add_argument(
        '--env', type=str, default='navigation'
    )
    parser.add_argument(
        '--agent_model', type=str, default='gpt-4o-mini'
    )
    parser.add_argument(
        '--max_trial', type=int, default=1,
        help='The max number of times to reflect for a single task'
    )
    parser.add_argument(
        "--train_temperature", type=float, default=0,
    )
    parser.add_argument(
        "--test_temperature", type=float, default=0,
    )
    parser.add_argument(
        "--manual_type", type=int, default=None,
    )
    parser.add_argument(
        "--imperfect_aware", type=str, default=None, choices=[None, 'general', 'specific']
    )
    parser.add_argument(
        "--hierachical", action="store_true",
    )
    parser.add_argument(
        "--exploration_model", type=str, default=None, 
    )
    parser.add_argument(
        "--note", type =str, default='',
    )
    parser.add_argument(
        "--debug", action="store_true",
    )

    args = parser.parse_args()

    # set log name
    str_debug = 'debug_' if args.debug else ''
    args.log_name = \
        f"{str_debug}{args.env}/Manual_{args.manual_type}_{args.hierachical}_{args.exploration_model}_{args.imperfect_aware}_{args.agent_model}_trial_{args.max_trial}"
    
    # set logging
    logger = Logger(args)

    # environment specific configs
    if 'Nav' in args.env:
        args.env_type = 'navigation'
    elif 'Cooking' in args.env:
        args.env_type = 'cooking'
    elif 'Roguelike' in args.env:
        args.env_type = 'roguelike'
        args.back = False
        if 'reversible' in args.env:
            args.back = True 
        
    with open(f'envs/env_configs/{args.env_type}.yaml', 'r') as file:
        yaml_args = yaml.safe_load(file)

    for key, value in yaml_args.items():
        setattr(args, key, value)

    # run main
    main(args=args, logger=logger)



# react: python main.py --env webshop
# react, cuterpg, no manual: python main.py
# react, cuterpg, perfect manual: python main.py --manual_type 1
# ..... desc .......... 2

# cache dir can be deleted; log may not



# python main.py --env VillageNav-NPC_mixed-hard-v0 --manual_type 2
# python main.py --env Cooking-easy-v0 --manual_type 2 --seed 1