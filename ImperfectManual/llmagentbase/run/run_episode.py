import numpy as np
from llmagentbase.reflection.reflexion import mem_to_reflection
from pdb import set_trace as st

def mem_to_reflect(trial, memory):
    reflection = ''
    if trial != 0:
        reflection += 'You have attempted this task multiple times before. Below are your previous reasonings and reflections. Carefully review them and avoid repeating the same mistakes:'
        for i in range(trial):
            curr = memory[2*i+1]
            reflection += f'\nTrial {i+1}: {curr}'
        reflection += '\n'
        # if trial == 2:
        #     st()
        # reflection = ReflectPrompt.format(reflection=reflection)
        # print(reflection)
        # st()
    return reflection

def run_one_episode(agent,
                    task_name,
                    trial,
                    memory,
                    logger,
                    args,
                    ):
    reward, traj, step_count = agent.run(task_name, 
                                         trial=trial,
                                         reflection=mem_to_reflect(trial, memory),
                                         args=args
                                         )

    logger.colored_log(f"Task {task_name}, trial {trial + 1}:", f"ends with reward: {reward:.3f}", color="cyan")
    # logger.save_gif(task_name, reward)
    # st()
    return traj, reward, step_count