
reason_prompt = """In this task, your goal is to navigate a map and reach a specified destination by taking appropriate actions. 
At each time step, you have the following inputs:
1. An observation showcasing the 3x3 tiles surrounding you, presented from a first-person perspective.
2. The direction you are currently facing.

You can issue the following actions in this environment:
    forward -> Move 1 tile forward in your current direction.
    turn right
    turn left
    turn around -> Rotate 180° to face the opposite direction.
    think[...] -> Use this to reason about your next move. Add any internal thoughts or planning here.

Movement Constraints:
    You can only move along the 'road'.
    Grass, trees, houses, and other obstacles are non-traversable.

At the same time, you received a step-by-step guide intended to help you complete this task. However, the guide is sometimes incorrect and does not perfectly match your current situation. Now, your state seems to be incorrect. Can you reason about why it may be incorrect. Observing your surroundings, what do you think is the best way for you to do as the next step then?
Example reasonings: 
Example 1: According to the guide, after walking forward 2 tiles I should see a snowman in the left tile. However, my current observation shows that the snowman is in the front-left tile. This mismatch indicates that the guide's description and my current state do not perfectly align. It is possible that the guide include the wrong number of steps. If I move one step further, I should be able to see the snowman on the left tile. Thus, the best next action is: move forward.
Example 2: According to the guide, I should move forward 3 tiles to approach the destination. I have moved forward for 3 times but the task hasn't finished yet. I can see that the destination is at my front-right tile, therefore moving forward one tile will bring me closer. Thus, the best next action is: move forward.
This is the step-by-step guide you have: {guide}
Here is your current trajectory:
{traj}
Now, please reason about what do you think is the best action for you to do as the next step:
Reasoning: """