nav_instruction_template = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination.
At each time step, you will be provided with the following inputs:
1. A first-person observation of the 3x3 surrounding tiles, with all unspecified tiles being {unspecified_tile}.
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
"""

nav_instruction_summer = nav_instruction_template.format(unspecified_tile='grasslands with flowers and scattered stones')
nav_instruction_winter = nav_instruction_template.format(unspecified_tile='lands with ice and scattered stones')


# python main.py --env VillageNav-easy-v0 --manual_type 1 --seed 12087226

nav_react = """
Here is one example:
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[I can't move forward because the tile ahead isn't a road. But since there's a road to my left, I can turn right and follow it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now that the tile in front of me is a road, I can move forward along it.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile in front of me is no longer a road, but there's a road to my left. I can try turning left to see what's over there.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[There's a road in front of me now, so I can walk forward and see what's ahead.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_tiles = """
Important: To assist you in this task, we provide a guide to find the destination.
Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 3 tiles (north).
Step 3. Turn left to face west.
Step 4. Move forward 2 tiles (west) to approach the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I'm facing north. According to the second step in the guide, I need to move forward three tiles in the direction to my left.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've moved forward once. According to the guide, I still need to move forward 3-1=2 more times.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've successfully moved forward three times. According to the next step in the guide, I need to turn left to face west. Since I'm currently facing north, turning left once will do it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to the fourth step in the guide, I need to move forward two tiles westward to approach the destination. So my next two actions will be to move forward twice.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_obs = """
Important: To assist you in this task, we provide a guide to find the destination.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Walk forward (toward north) until you see There is a group of green pines on the back-right tile. There is a house on the front-right tile. The front-left, left, right, back tiles are roads that you can step on.
Step 3. Turn left until you are facing west.
Step 4. Walk forward (toward west) until you are close to the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[According to Step 2, I need to walk forward (toward north) until I see a group of green pines on the back-right tile and a house on the front-right tile. I'm facing north now, but I haven't seen those landmarks yet, so I should start moving forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I can see a group of green pines now, but they're on the front-right and right tiles — not exactly where the guide described. So I'll keep moving forward to see if I can find the exact spot the guide refers to.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I see a group of green pines on the back-right tile and a house on the front-right tile. The front-left, left, right, back tiles are also roads — exactly as described in the guide. That means I've reached the correct location, so it's time to move on to the next step. The guide says to turn left until I'm facing west. Since I'm currently facing north, one left turn will do.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[I'm now facing west. The final instruction says to walk forward toward the west until I'm close to the destination. So I'll keep moving straight ahead.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""


nav_react_turns = """
Important: To assist you in this task, we provide a guide to find the destination.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Continue going north; turn left at the 1st opportunity.
Step 3. Go straight — your destination is just ahead, before any intersections.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[According to the guide, I need to continue going north and turn left at the first opportunity. So I'll keep moving forward until I find that the tile to my left is a road.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile to my left isn't a road yet, so I'll keep moving forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile to my left is now a road, so I should turn left here.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to Step 3 in the guide — 'Go straight; your destination is just ahead, before any intersections' — I should just keep moving forward now. I'll walk straight for a few steps.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""

nav_tiles_obs = """Important: To assist you in this task, we provide a guide to find the destination.
Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 3 tiles (north), after that you will see a group of green pines on the back-right tile and a house on the front-right tile.
Step 3. Turn left to face west.
Step 4. Move forward 2 tiles (west) to approach the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I'm facing north. According to the second step in the guide, I need to move forward three tiles in the direction to my left.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've moved forward once. According to the guide, I still need to move forward 3-1=2 more times.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've successfully moved forward three times. I can see that there are a group of green pines on the back-right tile and a house on the front-right tile, which matches the description in the guide exactly. According to the next step in the guide, I need to turn left to face west. Since I'm currently facing north, turning left once will do it.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to the fourth step in the guide, I need to move forward two tiles westward to approach the destination. So my next two actions will be to move forward twice.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully."""

nav_turns_obs =  """
Important: To assist you in this task, we provide a guide to find the destination.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Continue going north; turn left at the 1st opportunity. After that, you will see a house on the front-right tile and the front-left, left, right, back tiles are roads that you can step on.
Step 3. Go straight — your destination is just ahead, before any intersections.

Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines on the front-left tile.
The front-right, left, right tiles are roads that you can step on.
Direction: You are facing east.

Action: think[The first step in the guide is to turn left to face north. Since I'm currently facing east, turning left once will orient me toward the north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the front-left tile.
There is a group of green pines on the front-right tile.
The front, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: think[According to the guide, I need to continue going north and turn left at the first opportunity. So I'll keep moving forward until I find that the tile to my left is a road.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile to my left isn't a road yet, so I'll keep moving forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[The tile to my left is now a road, so this is the first possible left turn. I can also see that there is a house on the front-right tile, and the front-left, left, right, and back tiles are all roads, confirming that this is the correct place to turn. Therefore, I will turn left here.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-left tile.
There is a house on the back-right tile.
The front, front-right, left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: think[According to Step 3 in the guide — 'Go straight; your destination is just ahead, before any intersections' — I should just keep moving forward now. I'll walk straight for a few steps.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
The front, right, back-left, back tiles are roads that you can step on.
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""

nav_reflexion_template = """You are navigating through a map to reach a destination.
In the previous attempt, you failed. Carefully review the trajectory below, identify the likely cause of failure, and write a reflection that will help guide your next attempt.

Please respond in the following format:
Reason: ...
Reflection: ...

{extra}
Your response must be concise and under 256 tokens."""


general_reasons = """Common failure reasons include:
1. Repeating the same locations or actions without progress.
2. Getting stuck in a loop of invalid actions or unproductive thoughts."""
nav_reflexion = nav_reflexion_template.format(extra=general_reasons)

guide_reasons = f"""{general_reasons}
Since a guidance instruction is also provided, you should additionally consider:
3. The agent may not be following the guidance correctly.
4. The guidance may contain errors or be incomplete, and the agent failed to recognize and adapt to these issues."""

nav_reflexion_guide = nav_reflexion_template.format(extra=guide_reasons)


nav_plan_instruction_template = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination. You are going to be provided with a 'Current subgoal' to accomplish. 
At each time step, you will also be provided with the following inputs:
1. A first-person observation of the 3x3 surrounding tiles, with all unspecified tiles being {unspecified_tile}.
2. The direction you are currently facing.
Here are more detailed explanations of the observation you get:
1. You are positioned at the center tile of the 3x3 tiles.

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.
    stop -> issue this action when you think your current subgoal is accomplished. 

Movement Constraints:
    You can only move along the 'road'.
    Grass, trees, houses, and other obstacles are non-traversable.

Note: make sure to accomplish the subgoal within 10 actions. 
"""

nav_plan_instruction_summer = nav_plan_instruction_template.format(unspecified_tile='grasslands with flowers and scattered stones')
nav_plan_instruction_winter = nav_plan_instruction_template.format(unspecified_tile='lands with ice and scattered stones')



nav_subgoal = """
Current subgoal: move forward for 3 tiles.
Trajectory: 
Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the left tile.
There is a group of green pines that spans the front-right, right tiles.
The front, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've moved forward once. According to the guide, I still need to move forward 3-1=2 more times.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[I've successfully moved forward three times, therefore my current subgoal is achieved. I should issue a stop action now. ]
Observation: OK.

Action: stop
"""