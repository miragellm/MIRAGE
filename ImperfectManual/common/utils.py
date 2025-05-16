import random
import wandb
import numpy as np
from collections import Counter
from pdb import set_trace as st

def set_seed(seed) -> None:
    """Sets random seed for reproducibility
    Args:
        seed (int): Target seed to set
    """
    random.seed(seed)
    np.random.seed(seed)
    # import torch
    # torch.manual_seed(seed)
    # if torch.cuda.is_available():
    #     torch.cuda.manual_seed_all(seed)

def error_handle(signum, frame):
    """Time limit error handle"""
    raise Exception("Oops time is up")


def initialize_logs(task_range):
    last_rewards = []
    best_rewards = []
    best_trials = []
    prev_reflections = [[] for _ in range(len(task_range))]
    return last_rewards, best_rewards, best_trials, prev_reflections


def get_rew_and_sr(rewards, total_task=None, success_fn=lambda r: r == 1):
    """
    Compute average reward and success rate, with flexible success criteria.

    Args:
        rewards (List[float]): List of reward values.
        total_task (int, optional): Total number of tasks. If None, use len(rewards).
        success_fn (Callable): Function to determine whether a reward counts as success.

    Returns:
        Tuple[float, float]: (average reward, success rate)
    """
    total = total_task if total_task is not None else len(rewards)
    avg_reward = np.sum(rewards) / total
    success_rate = np.sum([1 for r in rewards if success_fn(r)]) / total
    return avg_reward, success_rate


def rew_logging(best_rewards, 
                last_rewards,
                best_trials,
                reward,
                task_idx,
                trial,
                logger,
                success_fn=lambda r: r == 1,
                debug=False,
                ):
    if trial == 0:
        last_rewards.append([])
        best_rewards.append(0)
        best_trials.append(0)

    last_rewards[-1].append(reward)
    logger.log('print', "*************************")

    if reward > best_rewards[-1]:
        best_rewards[-1] = reward
        best_trials[-1] = trial
        
    lasts = [x[trial] if trial < len(x) else x[-1] for x in last_rewards]

    (last_avg_r, last_sr) = get_rew_and_sr(lasts, success_fn=success_fn)
    (best_avg_r, best_sr) = get_rew_and_sr(best_rewards, success_fn=success_fn)

    logger.colored_log(
        f"Task {task_idx + 1}:",
        f"Average last reward: {last_avg_r:.3f}, average last success rate: {last_sr:.3f}",
        color="yellow"
    )
    logger.colored_log(
        f"Task {task_idx + 1}:",
        f"Average best reward: {best_avg_r:.3f}, average best success rate: {best_sr:.3f}",
        color="green"
    )
    if not debug:
        wandb.log({f'last rew trial {trial}': last_avg_r, 
                f'best rew trial {trial}': best_avg_r,
                f'last sr trial {trial}': last_sr,
                f'best sr trial {trial}': best_sr})

    return best_rewards, best_trials, last_rewards


def compute_accuracies(mode_recs, logger):
    if not mode_recs:
        return
    
    counter = Counter()

    for gt_mode, mode in mode_recs:
        if gt_mode == "N/A":
            continue
        counter['total'] += 1
        if gt_mode == mode:
            counter['correct'] += 1
            counter[f'{gt_mode}_correct'] += 1
        counter[f'{gt_mode}_total'] += 1

    overall_acc = counter['correct'] / counter['total'] if counter['total'] else 0
    explore_acc = counter['Explore_correct'] / counter['Explore_total'] if counter['Explore_total'] else 0
    follow_acc = counter['Follow_correct'] / counter['Follow_total'] if counter['Follow_total'] else 0

    accuracies = {
        'overall_accuracy': overall_acc,
        'explore_accuracy': explore_acc,
        'follow_accuracy': follow_acc
    }
    
    logger.log(f"\033[33mOverall Accuracy: \033[0m\033[32m{accuracies['overall_accuracy']:.2%}\033[0m")
    logger.log(f"\033[33mExplore Accuracy: \033[0m\033[32m{accuracies['explore_accuracy']:.2%}\033[0m")
    logger.log(f"\033[33mFollow Accuracy: \033[0m\033[32m{accuracies['follow_accuracy']:.2%}\033[0m")

    return 
