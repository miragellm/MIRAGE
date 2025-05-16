navigation_instruction = """In this task, you will navigate through a map with the goal of generating actions to locate and reach the destination.
At each time step, you will be provided with the following inputs:
1. An 18×18 matrix representing the 3x3 tiles surrounding you, displayed from a first-person perspective.
2. The direction you are currently facing.
Here are more detailed explanations of the observation you get:
1. You are positioned at the center of the matrix, and the top of the matrix aligns with your current “forward” direction.
2. Each tile consists of 6 grids, and the entries in the matrix describe the objects located at each grid.
    void -> Represents areas outside the map boundary.
    destination -> Marks the destination house you are aiming to reach.
    Consecutive object_233 entries -> Indicate that the area is occupied by object_233 (e.g., flowers, stones, etc.).

You can issue the following actions in this environment:
    forward -> Move 1 tile (6 grid spaces) forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.

Movement Constraints:
    You can only move along the 'road'. If there are not six consecutive grids of road directly in front of you, you cannot move forward.
    Grass, trees, houses, and other obstacles are non-traversable.
"""

navigation_react = """
Observation: void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
road road road road road road road road road road road road road road road road road road
road road road road road road road road road road road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road road road road road road road road road road road road
grass grass grass grass grass grass grass grass grass grass grass grass road road road road road road
object_163 land land object_40 land land object_114 land land land land grass road road road road road road
object_70 object_87 land object_148 land object_233 object_233 land object_96 object_151 land grass road road road road road road
object_70 object_77 object_77 object_71 object_71 object_233 object_233 land object_212 object_212 object_58 grass road road road road road road
land object_77 object_77 object_71 object_71 object_233 object_233 land object_212 object_212 object_148 grass road road road road road road
object_233 object_233 land land land object_233 object_233 object_84 object_212 object_212 land grass road road road road road road
Direction: You are facing east.

Action: think[I am at the center of the scene above, viewing it from a first-person perspective. I'm on a paved road stretching horizontally from left to right. Since the area in front is all void, marking the edge of the map, I will turn right and move forward along the road to explore further.]
Observation: OK.

Action: turn right
Observation: void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road grass grass grass grass grass grass
void void void void void void road road road road road road grass land land object_58 object_148 land
void void void void void void road road agent agent agent road grass land object_151 object_212 object_212 object_212
void void void void void void road road agent agent agent road grass land object_96 object_212 object_212 object_212
void void void void void void road road agent agent agent road grass land land land land object_84
void void void void void void road road road road road road grass object_114 object_233 object_233 object_233 object_233
void void void void void void road road road road road road grass land object_233 object_233 object_233 object_233
void void void void void void road road road road road road grass land land object_71 object_71 land
void void void void void void road road road road road road grass object_40 object_148 object_71 object_71 land
void void void void void void road road road road road road grass land land object_77 object_77 land
void void void void void void road road road road road road grass land object_87 object_77 object_77 object_233
void void void void void void road road road road road road grass object_163 object_70 object_70 land object_233
Direction: You are facing south.

Action: forward
Observation: void void void void void void land land land land destination destination destination destination destination destination destination destination
void void void void void void object_85 land land land destination destination destination destination destination destination destination destination
void void void void void void object_252 object_252 object_136 object_136 destination destination destination destination destination destination destination destination
void void void void void void object_252 object_252 object_136 object_136 destination destination destination destination destination destination destination destination
void void void void void void object_147 land land object_46 destination destination destination destination destination destination destination destination
void void void void void void grass grass grass grass destination destination destination destination destination destination destination destination
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road grass grass grass grass grass grass
void void void void void void road road road road road road grass land land object_58 object_148 land
void void void void void void road road road road road road grass land object_151 object_212 object_212 object_212
void void void void void void road road road road road road grass land object_96 object_212 object_212 object_212
void void void void void void road road road road road road grass land land land land object_84
void void void void void void road road road road road road grass object_114 object_233 object_233 object_233 object_233
Direction: You are facing south.

Action: think[I am at the center of the scene above, viewing it from a first-person perspective. I can see the destination ahead to my right. To get closer, I will turn right and move forward along the road.]
Observation: OK.

Action: turn right
Observation: destination destination destination destination destination destination road road road road road road grass land object_212 object_212 object_84 object_233
destination destination destination destination destination destination road road road road road road grass object_148 object_212 object_212 land object_233
destination destination destination destination destination destination road road road road road road grass object_58 object_212 object_212 land object_233
destination destination destination destination destination destination road road road road road road grass land object_151 object_96 land object_233
destination destination destination destination destination destination road road road road road road grass land land land land object_114
destination destination destination destination destination destination road road road road road road grass grass grass grass grass grass
destination destination destination destination destination destination road road road road road road road road road road road road
destination destination destination destination destination destination road road agent agent agent road road road road road road road
land land object_136 object_136 object_46 grass road road agent agent agent road road road road road road road
land land object_136 object_136 land grass road road agent agent agent road road road road road road road
land land object_252 object_252 land grass road road road road road road road road road road road road
land object_85 object_252 object_252 object_147 grass road road road road road road road road road road road road
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
Direction: You are facing west.

Action: forward
Task completed successfully.
"""


navigation_react_perfect = """
Important: To assist you in this task, we provide a perfect guide. Please follow this guide step by step.
Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1: Turn right to face south.
Step 2: Move forward 1 tile (south).
Step 3: Turn right to face west.
Step 4: Move forward 1 tile (west) to approach the destination.

Try your best to navigate to the destination:
Observation: void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
road road road road road road road road road road road road road road road road road road
road road road road road road road road road road road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road agent agent agent road road road road road road road road
road road road road road road road road road road road road road road road road road road
grass grass grass grass grass grass grass grass grass grass grass grass road road road road road road
object_163 land land object_40 land land object_114 land land land land grass road road road road road road
object_70 object_87 land object_148 land object_233 object_233 land object_96 object_151 land grass road road road road road road
object_70 object_77 object_77 object_71 object_71 object_233 object_233 land object_212 object_212 object_58 grass road road road road road road
land object_77 object_77 object_71 object_71 object_233 object_233 land object_212 object_212 object_148 grass road road road road road road
object_233 object_233 land land land object_233 object_233 object_84 object_212 object_212 land grass road road road road road road
Direction: You are facing east.

Action: think[I am at the starting point of the task, currently facing east. According to the step-by-step guide, the first instruction is to turn right until I'm facing south. Since I am facing east, turning right once will align me with the correct direction. Therefore, my next action should be to turn right to face south.]
Observation: OK.

Action: turn right
Observation: void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road grass grass grass grass grass grass
void void void void void void road road road road road road grass land land object_58 object_148 land
void void void void void void road road agent agent agent road grass land object_151 object_212 object_212 object_212
void void void void void void road road agent agent agent road grass land object_96 object_212 object_212 object_212
void void void void void void road road agent agent agent road grass land land land land object_84
void void void void void void road road road road road road grass object_114 object_233 object_233 object_233 object_233
void void void void void void road road road road road road grass land object_233 object_233 object_233 object_233
void void void void void void road road road road road road grass land land object_71 object_71 land
void void void void void void road road road road road road grass object_40 object_148 object_71 object_71 land
void void void void void void road road road road road road grass land land object_77 object_77 land
void void void void void void road road road road road road grass land object_87 object_77 object_77 object_233
void void void void void void road road road road road road grass object_163 object_70 object_70 land object_233
Direction: You are facing south.

Action: think[I have successfully turned right and am now facing south, as instructed. According to the guide, the next step is to move forward 1 tile. Observing my surroundings, I can see that I'm on a vertical road with a clear path ahead. Since the road continues in front of me, I can safely proceed. Therefore, my next action is to move forward.]
Observation: OK.

Action: forward
Observation: void void void void void void land land land land destination destination destination destination destination destination destination destination
void void void void void void object_85 land land land destination destination destination destination destination destination destination destination
void void void void void void object_252 object_252 object_136 object_136 destination destination destination destination destination destination destination destination
void void void void void void object_252 object_252 object_136 object_136 destination destination destination destination destination destination destination destination
void void void void void void object_147 land land object_46 destination destination destination destination destination destination destination destination
void void void void void void grass grass grass grass destination destination destination destination destination destination destination destination
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road agent agent agent road road road road road road road
void void void void void void road road road road road road road road road road road road
void void void void void void road road road road road road grass grass grass grass grass grass
void void void void void void road road road road road road grass land land object_58 object_148 land
void void void void void void road road road road road road grass land object_151 object_212 object_212 object_212
void void void void void void road road road road road road grass land object_96 object_212 object_212 object_212
void void void void void void road road road road road road grass land land land land object_84
void void void void void void road road road road road road grass object_114 object_233 object_233 object_233 object_233
Direction: You are facing south.

Action: think[I am still on the vertical road, facing south. According to the guide, the next steps are to turn right to face west and then move forward 1 tile. Turning right from my current position will align me with the west direction. In my current observation, I can see the destination located at my front-right, confirming that this is the correct path. After the turn, the horizontal road ahead is clear, allowing me to proceed safely. Therefore, I will first turn right to face west and then move forward 1 tile, bringing me closer to the destination and following the guide accurately.]
Observation: OK.

Action: turn right
Observation: destination destination destination destination destination destination road road road road road road grass land object_212 object_212 object_84 object_233
destination destination destination destination destination destination road road road road road road grass object_148 object_212 object_212 land object_233
destination destination destination destination destination destination road road road road road road grass object_58 object_212 object_212 land object_233
destination destination destination destination destination destination road road road road road road grass land object_151 object_96 land object_233
destination destination destination destination destination destination road road road road road road grass land land land land object_114
destination destination destination destination destination destination road road road road road road grass grass grass grass grass grass
destination destination destination destination destination destination road road road road road road road road road road road road
destination destination destination destination destination destination road road agent agent agent road road road road road road road
land land object_136 object_136 object_46 grass road road agent agent agent road road road road road road road
land land object_136 object_136 land grass road road agent agent agent road road road road road road road
land land object_252 object_252 land grass road road road road road road road road road road road road
land object_85 object_252 object_252 object_147 grass road road road road road road road road road road road road
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
void void void void void void void void void void void void void void void void void void
Direction: You are facing west.

Action: forward
Observation: Task completed successfully.
"""

navigation_react_descriptive = "to be implemented"
navigation_react_stepwise = """placeholder for now"""
navigation_reflexion = """placeholder for now"""