import pygame
from common.utils import set_seed, rew_logging, initialize_logs, compute_accuracies
from envs.utils import load_env
from llmagentbase.run.run_episode import run_one_episode
from llmagentbase.prompts import get_prompt
from llmagentbase.agent import build_agent
from llmagentbase.reflection.reflexion import reflect
from llmagentbase.utils import log_trial, log_task
from pdb import set_trace as st

def collect_trajs(  task_range,
                    logger,
                    max_trial,
                    args,
                    is_train,
                    ):
    # set_seed(args.seed)
    env = load_env(args, is_train)
    # get prompts
    instruction = get_prompt('instruction', env, args)
    in_context = get_prompt('react', env, args)
            
    last_rewards, best_rewards, best_trials, prev_reflections = initialize_logs(task_range)
    # init agent
    agent = build_agent(None,
                        instruction,
                        in_context,
                        logger,
                        args.train_temperature if is_train else args.test_temperature,
                        args)
    if args.env_type == 'roguelike':
        success_fn = lambda r: r != 0
    else:
        success_fn = lambda r: r == 1
    
    for task_idx, task_name in enumerate(task_range):
        log_task(task_idx, task_name, logger)
        for trial in range(max_trial): #loop in this way because of the way alfworld loops
            # load env for agent
            agent.env = env
            log_trial(trial, logger) #log trial information
            # really run one task
            traj, reward, step_count = run_one_episode(  agent,
                                                        task_name=task_name,
                                                        trial=trial,
                                                        memory=prev_reflections[task_idx],
                                                        logger=logger,
                                                        args=args,
                                                        )
            compute_accuracies(agent.mode_recs, logger)
            success = success_fn(reward)
            logger.log_experiment(step_count, success)

            traj_reflection = ''
            #only reflect on failed trajectories 
            if trial < max_trial - 1 and (not success) and args.agent_model != 'human':
                traj_reflection = reflect(  traj,
                                            args.env,
                                            args.agent_model,
                                            get_prompt('reflexion', env, args),
                                            logger,
                                            )

            prev_reflections[task_idx].extend([traj, traj_reflection])
            best_rewards, best_trials, last_rewards = rew_logging(best_rewards,
                                                                  last_rewards,
                                                                  best_trials,
                                                                  reward,
                                                                  task_idx,
                                                                  trial=trial,
                                                                  logger=logger,
                                                                  success_fn=success_fn,
                                                                  debug=args.debug)
            if success:
                break

        logger.save_gif(task_name, best_rewards[-1])
        agent.close_env()

    logger.save_summary()
    return