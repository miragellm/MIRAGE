from common.llms import llm
from pdb import set_trace as st

def mem_to_reflection(memory):
    if len(memory) == 0:
        return ''
    assert len(memory) % 2 == 0, 'One of the trajectory does not have a reflection with it. '
    n_trial_cap = 3 # this is to avoid the prompt being too long, therefore for repeat >= 5, may perform worse. 
    memory = memory[-2*n_trial_cap:]
    prompt = ''
    for i in range(min(n_trial_cap, len(memory)//2)):
        reflection = memory[2*i+1]
        prompt += f'Reflection on failed attempt {i+1}: \n{reflection}\n'
    return prompt

def reflect(traj,
            env_type,
            reflect_model,
            in_context,
            logger):
    prompt = f"{in_context}\n{traj}\nReason:"
    reflection = llm(   prompt, 
                        reflect_model, 
                        temperature=0, 
                        max_tokens=256, 
                        stop=None)
    logger.log(f'\n\033[33mReflection\033[0m: {reflection}')
    return reflection