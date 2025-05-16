import yaml
import numpy as np

import gym

from pdb import set_trace as st

from envs.cuterpg import *
    

def is_env_registered(env_id):
    """Check if an environment is already registered in Gym."""
    return env_id in gym.envs.registry.env_specs


def get_task_range(args, is_train=False):
    if is_train:
        task_range = [i for i in range(args.n_train_tasks)]
    else:
        task_range = [i for i in range(args.n_test_tasks)]
    return list(task_range)

def load_env(args, is_train=False):
    if is_env_registered(args.env):
        env = gym.make(args.env)
    else:
        st()
    return env
