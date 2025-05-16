p_mode_switch = """In this task, your goal is to navigate a map and reach a specified destination by taking appropriate actions. You will receive a step-by-step guide to help you complete this task. However, the guide may sometimes be incorrect or not perfectly match your current situation. 
Your job is to carefully check if the guide aligns with your current observation and decide whether to follow or explore.

At each decision point, clearly indicate whether you should 
1. follow the guide exactly (Follow mode)
2. deviate from it and explore your surroundings (Explore mode).

Respond using the following format:
Mode: <clearly describe your current step, summarize your situation, and provide reasoning for your decision>. Therefore, my current mode should be: <Follow/Explore>.

Here is an example:
Step-by-Step Guide to complete the task: 
Start! You are currently facing east.
Step 1. Turn right until you are facing south.
Step 2. Walk forward (toward south) 2 tiles, after that you will see There is a orange tree with a hollow trunk on the back-left tile and The front, front-right, left, back tiles are roads that you can step on.
Step 3. Turn left until you are facing east.
Step 4. Walk forward (toward east) 1 tile to get close to the destination.

Trajectory:
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the back, back-right tiles.
There is a cluster of red firs that spans the front, front-right tiles.
There is a house on the back-right tile.
The right tile is road that you can step on.
There is a orange tree with a hollow trunk on the front-right tile.
The front-left, left, back-left tiles are out of the map boundary.
Direction: You are facing east.

Mode: I'm currently at Step 1, which instructs me to turn right until facing south. My current direction is east, and turning right from east once would correctly orient me south, matching the instruction. Therefore, my current mode should be: Follow.

Action: think[I want to follow the step 1 of the guide. the first instruction is to turn right until I'm facing south. Since I am facing east, turning right once will align me with the correct direction. Therefore, my next action should be to turn right to face south.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs that spans the front-right, right tiles.
There is a cluster of red firs that spans the front-left, left tiles.
There is a house on the front-right tile.
The front tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the front-left tile.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing south.

Mode: I'm now facing south, meaning that I have completed Step 1. At Step 2, I need to walk forward (south) two tiles. My front tile is road, meaning that I'm able to follow Step 2 to forward. Therefore, my current mode should be: Follow.

Action: think[I want to follow the step 2 of the guide. According to the guide, the next step is to forward 2 tiles. Observing my surroundings, I can see that the front tile is road, so I can safely proceed. Therefore, my next action is forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs that spans the right, back-right tiles.
There is a cluster of red firs that spans the left, back-left tiles.
There is a house that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk that spans the front-left, left tiles.
Direction: You are facing south.

Mode: I'm still at Step 2, where I need to move forward (south) two tiles. I've moved forward one tile and need to move forward for another 2-1=1 tile. I can see that my front tile is still road so this action is possible. Therefore, my current mode should be: Follow.

Action: think[I have successfully moved forward, according to the instructions I need to move forward 2 times. Now I still need to move forward for 2-1=1 step. Observing my surroundings, I can see that the front tile is road, so I can safely proceed. Therefore, my next action is forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs on the back-right tile.
There is a cluster of red firs on the back-left tile.
There is a house that spans the front-right, right, back-right tiles, the front-left, front, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk that spans the left, back-left tiles, and
Direction: You are facing south.

Mode: I've moved forward 2 tiles following step 2. However, in step 2 it says after moving forward 2 tiles I will see 'a orange tree with a hollow trunk on the back-left tile and the front, front-right, left, back tiles are roads'. However, this does not match my current observation. For example, the current front-right is a house, not road. I think maybe the number of tiles written in step 2 is wrong. I need to explore around to find the desired observation before moving to step 3. Therefore, my current mode should be: Explore.

Action: think[After exploring around with multiple agents, the best sequence of future actions that I think will guide me back to the correct path is forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
The destination is on the front-left tile.
There is a house that spans the right, back-right tiles.
The front, front-right, left, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the back-left tile.
Direction: You are facing south.

Mode: After moving forward one step, my current observation now fully matches the conditions described at the end of Step 2: the orange tree is on my back-left tile, and the tiles at front, front-right, left, and back are all roads. This confirms that I've successfully completed Step 2 and am now ready to proceed to Step 3. Therefore, my current mode should be: Follow.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you: 
The destination is on the front-right tile.
There is a house that spans the back-left, back tiles.
The front, left, right, back-right tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the front-left tile.
Direction: You are facing east.

Mode: I've completed Step 3 and am now facing east. According to Step 4, I should walk forward (toward east) 1 tile to get close to the destination. My front tile is road so I can forward. Therefore, my current mode should be: Follow.

Action: forward
Observation: Task completed successfully.

Now it's your turn:
Step-by-Step Guide to complete the task:
{manual}
Trajectory:
{traj}
Mode: """


# explore_subgoal = """In this task, your goal is to navigate a map and reach a specified destination by taking appropriate actions. 
# At each time step, you have the following inputs:
# 1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
# 2. The direction you are currently facing.

# You received a step-by-step guide intended to help you complete this task. However, the guide may not always be perfectly accurate or fully aligned with your current situation. Therefore, your goal now is to propose multiple possible action plans to carefully examine your surroundings. Each plan should consist of one or more actions.

# You can issue the following actions in this environment:
#     forward -> Move 1 tile forward in your current direction.
#     turn right
#     turn left
#     turn around -> Rotate 180° to face the opposite direction.

# Movement Constraints:
#     You can only move along the 'road'.
#     Grass, trees, houses, and other obstacles are non-traversable.

# Required answer format:
# 1. List 3-4 distinct exploration plans using the following structured format:
# Plan [index]:
# Reasoning: ...
# Purpose: [Clearly state purpose with enough details. Important: later on when doing exploration, you will only have access to this plan, not the guide itself, therefore information like desired observations should be very clear.]
# Potential Action Sequence: ...
# 2.	Your first proposed exploration plan, which is Plan 1, should be the action sequence following the step-by-step guide directly. While the other plans should assume that there is something incorrect with the guide, so you need to explore the surrondings. 

# Example answer (we omit the trajectory and manual for the example for simplicity):
# Answer: the current state does not match the guide because according to the guide, after walking forward 6 tiles I will see the following observations: a cluster of orange firs that spans the front-right, right tiles and a tower that spans the front-left, left tiles. However currently, my left tile is a house, not a tower.

# Plan 1:
# Reasoning: I should strictly follow the step-by-step guide. Now I'm on the step 3 of the guide. 
# Purpose: I have move forward along this direction for 2 tiles. Following step 3 of the guide, I should now move forward for another 3-2=1 tile.
# Potential Action Sequence: move forward once. 

# Plan 2:
# Reasoning: The guide tells me to move forward. However, my front tile is not road and I can only move along the 'road' tiles. I think maybe I turned too early. My front-left tile is a road tile, therefore maybe I should have move forward for more tiles.
# Purpose: I need to turn left and move forward to check if that tile matches the description in the guide: which has a cluster of orange firs that spans the front-right, right tiles and there is a tower that spans the front-left, left tiles. If yes, I can turn right there.
# Potential Action Sequence: turn left, forward, turn right, forward. 

# Plan 3:
# Reasoning: Based on my trajectory history, I once saw a tower on my way here, it's possible that the number of tiles in the guide is wrong and I should have moved forward for less than 3 tiles. 
# Purpose: Go back to the previous tiles, to check if any tiles on my way here have a cluster of orange firs that spans the front-right, right tiles and there is a tower that spans the front-left, left tiles if facing north (the current direction).
# Potential Action Sequence: turn around, move forward for a few times (less than 6 times), when I see a cluster of orange firs that spans the back-left, left tiles and there is a tower that spans the back-right, right tiles, I will turn around.
# ...

# This is the step-by-step guide you have:
# {guide}

# Here is your current trajectory:
# {traj}

# Now, please summarize the discrepancy and generate your plans.
# Answer: """

explore_subgoal = """In this task, your goal is to navigate a map and reach a specified destination by taking appropriate actions. 
At each time step, you have the following inputs:
1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
2. The direction you are currently facing.

You received a step-by-step guide intended to help you complete this task. However, the guide may not always be perfectly accurate or fully aligned with your current situation. Therefore, your goal now is to propose multiple possible action plans to carefully examine your surroundings. Each plan should consist of one or more actions.

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.

Movement Constraints:
    You can only move along the 'road'.
    Grass, trees, houses, and other obstacles are non-traversable.

Required answer format:
1. List at most 5 distinct exploration plans using the following structured format:
Plan [index]:
Reasoning: ...
Purpose: [Clearly state purpose with enough details. Important: later on when doing exploration, you will only have access to this plan, not the guide itself, therefore information like desired observations should be very clear.]
Potential Action Sequence: ...
2.	Your first proposed exploration plan, which is Plan 1, should be the action sequence following the step-by-step guide directly. While the other plans should assume that there is something incorrect with the guide, so you need to explore the surrondings. 

Example answer (we omit the trajectory and manual for the example for simplicity):
Answer: the current state does not match the guide because according to the guide, after walking forward 6 tiles I will see the following observations: a cluster of orange firs that spans the front-right, right tiles and a tower that spans the front-left, left tiles. However currently, my left tile is a house, not a tower.

Plan 1:
Reasoning: I should strictly follow the step-by-step guide. Now I'm on the step 3 of the guide. 
Purpose: I have move forward along this direction for 2 tiles. Following step 3 of the guide, I should now forward for another 3-2=1 tile.
Potential Action Sequence: forward.

Plan 2:
Reasoning: The guide indicates that I should see a cluster of orange firs that spans the front-right, right tiles and a tower that spans the front-left, left tiles after moving forward 3 tiles, however, this does not match my current observation. I can see a cluster of orange firs on my front-right, but not right tiles, therefore maybe I should move forward for one more tile to see if the observation above totally match the description in the guide. 
Purpose: I need to move forward to check if that tile matches the description in the guide: which has a cluster of orange firs that spans the front-right, right tiles and there is a tower that spans the front-left, left tiles. If yes, I can turn right there.
Potential Action Sequence: forward, turn right, forward. 

Plan 3:
Reasoning: Based on my trajectory history, I once saw a tower on my way here, it's possible that the number of tiles in the guide is wrong and I should have moved forward for less than 3 tiles. 
Purpose: Go back to the previous tiles, to check if any tiles on my way here have a cluster of orange firs that spans the front-right, right tiles and there is a tower that spans the front-left, left tiles if facing north (the current direction).
Potential Action Sequence: turn around, forward for a few times (less than 6 times), when I see a cluster of orange firs that spans the back-left, left tiles and there is a tower that spans the back-right, right tiles, I will turn around.
...

This is the step-by-step guide you have:
{guide}

Here is your current trajectory:
{traj}

Now, please summarize the discrepancy and generate your plans.
Answer: """

follow_subgoal = """You are an intelligent agent navigating a grid-based environment.

At each time step, you have the following inputs:
1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
2. The direction you are currently facing.
3. A plan that you should follow.

Your task is to carefully follow the plan, taking one or more actions to carry it out.

Available actions:
- forward -> Move 1 tile forward in your current direction.
- turn left
- turn right
- turn around -> Rotate 180° to face the opposite direction.
- think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.
- stop -> please issue this stop action when you think you have completed the selected plan. 

Here is an example: 
Here is the selected plan to follow:
Purpose: Turn around and go back to check those tiles and see if one of the tile has tower on the right tile when I'm facing north (the current direction).
Potential Action Sequence: turn around, move forward for a few times (less than 6 times) until I see a tower on the left tile, then I can turn around, so the tower is on the right tile for the same direction. 

Trajectory:
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of orange firs on the back-left tile.
The back, left, right tiles are roads that you can step on.
The front-right, front, front-left tiles are out of the map boundary.
There is a tower on the back-right tile.
Direction: You are facing north.

Action: think[Based on the plan, I want to turn around and go back for a few steps until I see the tower on the left tile. Therefore the next action I will take is turn around]
Observation: OK.

Action: turn around
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of orange firs on the front-right tile.
The front, left, right tiles are roads that you can step on.
There is a tower on the front-left tile.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of orange firs that spans the front-right, right tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
There is a tower that spans the front-left, left tiles.
Direction: You are facing south.

Action: turn around
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of orange firs that spans the back-left, left tiles.
The back, front-right, front, front-left tiles are roads that you can step on.
There is a tower that spans the back-right, right tiles.
Direction: You are facing north.

Action: think[I can already see that the tower is on my right tile when I'm facing north. Therefore I have completed the subgoal, I can stop here.]
Observation: OK. 

Action: stop

Now it's your turn:
Here is the selected plan to follow:
{selected_plan}

Trajectory:
{traj}
Action: """


best_selection = """In this task, your goal is to navigate a map and reach a specified destination by taking appropriate actions. 
At each time step, you have the following inputs:
1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
2. The direction you are currently facing.
3. a step-by-step guide intended to help you complete this task. However, the guide may sometimes be incorrect or not perfectly match your current situation.

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.

After some actions, you sent out multiple agent to attempt multiple exploration strategies. Your task is to evaluate all the provided trajectories and determine which of the exploration strategy is the best. Directly tell me the corresponding index (1-indexing). Your answer format should be Reasoning: ... Answer: ...

For example: 
Example 1:
Reasoning: Based on my current trajectory, originally I failed to move forward after turning right following step 4 of the step-by-step guide. However, for plan 2, after I turn left and move forward for another tile, my right tile becomes a road road tile, making me able to move forward there after I turn right. Therefore I think the best exploration is done by 2. 
Answer: 2

Example 2:
Reasoning: The step-by-step guide step 2 instructs me to move forward for 3 tiles. I have move forward 1 tiles in the original trajectory. The best strategy seems to be Plan 1, which follows the guide to directly goes forward more times. Therefore I will follow plan 1. 
Answer: 1

Example 3:
Reasoning: The step-by-step guide step 1 instructs me to move forward for 3 tiles and turn towards north when I see a tower on the right tile. However, after moving forward 3 times, I didn't see the tower on the right tile, but it's on the front-right tile instead. Therefore, I think the original guide has the wrong number of tiles written in step 2. The best exploration strategy is Plan 3, which directly goes forward for another tile and then I see the tower at the right tile, which matches the description in the step 1 of the guide. Therefore I will follow this one. 
Answer: 3

This is the step-by-step guide you have: {guide}
Here is your current trajectory:
{traj}

Here are the exploration trajectories from this step and on:
{info}

Based on the exploration trajectories above, now which exploration strategy do you think is the best? (Makes you follow the step-by-step guide the best and fix any potential wrong information in the guide). Directly tell me the ID after reasoning. If none of them is good, answer 0. 
Reasoning: """



mode_action = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination.
At each time step, you will be provided with the following inputs:
1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
2. The direction you are currently facing.
Here are more detailed explanations of the observation you get:
1. You are positioned at the center tile of the 3x3 tiles.

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.

Movement Constraints:
    You can only move along the 'road'.
    Grass, trees, houses, and other obstacles are non-traversable.

Important: You are provided with a navigation guide to help you reach your destination. This guide offers directional steps and approximate distances. Please note that the guide is not perfectly accurate, the number of tiles to move forward may be slightly incorrect. However, it is generally correct (the overall direction is definitely correct), therefore you should use it wisely to find the destination!

Movement Rules:
1. You can move one tile per action.
2. If the guide instructs you to move multiple tiles (e.g., “walk forward 5 tiles”), you should execute that as five individual forward actions.

Here is an example:
Step-by-Step Guide to complete the task: 
Start! You are currently facing east.
Step 1. Turn right until you are facing south.
Step 2. Walk forward (toward south) 2 tiles, after that you will see There is a orange tree with a hollow trunk on the back-left tile and The front, front-right, left, back tiles are roads that you can step on.
Step 3. Turn left until you are facing east.
Step 4. Walk forward (toward east) 1 tile to get close to the destination.

Trajectory:
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of green firs that spans the back, back-right tiles.
There is a cluster of red firs that spans the front, front-right tiles.
There is a house on the back-right tile.
The right tile is road that you can step on.
There is a orange tree with a hollow trunk on the front-right tile.
The front-left, left, back-left tiles are out of the map boundary.
Direction: You are facing east.

Action: think[I want to follow the step 1 of the guide. the first instruction is to turn right until I'm facing south. Since I am facing east, turning right once will align me with the correct direction. Therefore, my next action should be to turn right to face south.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs that spans the front-right, right tiles.
There is a cluster of red firs that spans the front-left, left tiles.
There is a house on the front-right tile.
The front tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the front-left tile.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing south.

Action: think[I want to follow the step 2 of the guide. According to the guide, the next step is to move forward 2 tiles. Observing my surroundings, I can see that the front tile is road, at the same time, I'm current facing south, so I can safely proceed to move towards the correct direction. Therefore, my next action is to move forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs that spans the right, back-right tiles.
There is a cluster of red firs that spans the left, back-left tiles.
There is a house that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk that spans the front-left, left tiles.
Direction: You are facing south.

Action: think[I have successfully moved forward, according to the instructions I need to move forward 2 times. Now I still need to move forward for 2-1=1 step. Observing my surroundings, I can see that the front tile is road and I'm currently facing south, so I can safely proceed to move towards south. Therefore, my next action is to move forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
There is a cluster of green firs on the back-right tile.
There is a cluster of red firs on the back-left tile.
There is a house that spans the front-right, right, back-right tiles, the front-left, front, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk that spans the left, back-left tiles, and
Direction: You are facing south.

Action: think[I have followed the guide to move forward 2 tiles, however, my current observation does not match what's described in the guide for step 2. Therefore, I sent out multiple agents to explore around. Based on the exploration, the best sequence of future actions that will guide me back to the correct path is to move forward and then turn left.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you: 
The destination is on the front-left tile.
There is a house that spans the right, back-right tiles.
The front, front-right, left, back tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the back-left tile.
Direction: You are facing south.

Action: think[Now I can see now the observation matches what's described in the guide - I can see a orange tree with a hollow trunk on the back-left tile and the front, front-right, left, back tiles are roads. Now I'm back to the right track and successfully finish step 2 of the guide. Therefore, I can move on to step 3, which asks me to turn left.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you: 
The destination is on the front-right tile.
There is a house that spans the back-left, back tiles.
The front, left, right, back-right tiles are roads that you can step on.
There is a orange tree with a hollow trunk on the front-left tile.
Direction: You are facing east.

Action: think[Now I'm facing east, so I have successfully done with step 3. Now I can move on to step 4 of the guide, which instructs me to move forward. My front tile is road, therefore I can safely move forward to move towards east following step 4.]
Observation: OK.

Action: forward
Observation: Task completed successfully.
"""
