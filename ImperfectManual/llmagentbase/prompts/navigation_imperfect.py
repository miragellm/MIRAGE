
# for change of season
nav_season = """
Important: A guide is provided to help you find the destination, but it may not be fully reliable. For example, it might describe conditions from summer while you are navigating in winter.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Walk forward (toward north) until you see The destination is on the front-right tile. There is a cluster of a green conical tree and four round trees on the back-left tile. There is a house on the back-right tile. The front-left, front, right, back tiles are roads that you can step on.
Step 3. Turn right until you are facing east.
Step 4. Walk forward (toward east) until you are close to the destination.

Observation: You can see the 3x3 tiles surrounding you:
There is a house on the front-left tile.
The left, back-left tiles are roads that you can step on.
There is a smiling snowman with a carrot nose and coal buttons that spans the front-left, front tiles.
The front-right, right, back-right tiles are out of the map boundary.
Direction: You are facing east.

Action: think[I am currently facing east. The guide says “Turn left until you are facing north.” Turning left once from east will make me face north.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
There is a house on the front-right tile.
The front-left, front tiles are roads that you can step on.
There is a smiling snowman with a carrot nose and coal buttons that spans the front-right, right tiles.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing north.

Action: think[I am facing north. The guide says I should walk forward until I see a house on the front-right tile and roads on the front-left, front tiles. From my observation, I only see roads at the front-left and front, and a house and snowman at the front-right and right. The scene doesn't fully match the guide yet, so I should keep walking forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of a snow-covered conical tree and four snow-dusted round trees on the front-left tile.
There is a house that spans the front-right, right tiles.
The front, left, back tiles are roads that you can step on.
There is a smiling snowman with a carrot nose and coal buttons that spans the right, back-right tiles.
There is a plain snowman without any decorations on the front-left tile.
Direction: You are facing north.

Action: think[The guide expects a green conical tree and a house on the back-right, but now I see snow-covered trees and a house at the front-right and right. The details don't match yet, so I should keep walking forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a cluster of a snow-covered conical tree and four snow-dusted round trees on the left tile.
There is a house that spans the right, back-right tiles.
The front, front-right, back-left, back tiles are roads that you can step on.
There is a smiling snowman with a carrot nose and coal buttons on the back-right tile.
There is a plain snowman without any decorations that spans the front-left, left tiles.
Direction: You are facing north.

Action: think[I am facing north. The guide says the house should be on the back-right, but now it's on the right and back-right. Also, the cluster of trees is on the left, not the back-left. The scene still doesn't match, so I should keep walking forward.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-right tile.
There is a cluster of a snow-covered conical tree and four snow-dusted round trees on the back-left tile.
There is a house on the back-right tile.
The front-left, front, right, back tiles are roads that you can step on.
There is a plain snowman without any decorations that spans the left, back-left tiles.
Direction: You are facing north.

Action: think[The scene mostly matches the guide: the house is on the back-right, the roads are in the correct places, and the tree cluster is roughly correct despite seasonal differences. It's time to move to the next step: turn right to face east.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
The destination is on the front-left tile.
There is a cluster of a snow-covered conical tree and four snow-dusted round trees on the back-right tile.
There is a house on the front-right tile.
The front, left, right, back-left tiles are roads that you can step on.
There is a plain snowman without any decorations that spans the back, back-right tiles.
Direction: You are facing east.

Action: think[I am facing east now. The guide instructs me to walk forward toward the destination. The destination is currently on my front-left, and the tile directly in front of me is a road. I should walk forward to get closer to the destination.]
Observation: OK.

Action: forward
Observation: Task completed successfully.
"""

wrong_turn_obs = """Important: You are provided with a guide to help you find the destination. However, the number of turns to take may not be perfectly accurate. To assist you, additional landmarks such as trees, houses, and other objects are given as reliable indicators.

Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left until you are facing north.
Step 2. Continue going north; turn left at the 2nd opportunity. After that, you will see a house on the front-right tile and the front-left, left, right, back tiles are roads that you can step on.
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

Action: think[According to the guide, I need to continue going north and turn left at the second opportunity. So I'll keep moving forward until I find that the tile to my left is a road.]
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

Action: think[The tile to my left is a road, which makes it the first possible turn. Although the guide says to turn at the second opportunity, it also mentioned that the number might be inaccurate. Now, I can see a group of green pines on the back-right tile and a house on the front-right tile, exactly as the guide described. Therefore, I believe it's reasonable to turn left here.]
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

wrong_tile_obs = """Important: You are provided with a guide to help you find the destination. However, the number of tiles may not be perfectly accurate. To assist you, additional landmarks such as trees, houses, and other objects are given as reliable indicators.

Note that you can only move one tile per action. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Turn left to face north.
Step 2. Move forward 2 tiles (north), after that you will see a group of green pines on the back-right tile and a house on the front-right tile.
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

Action: think[I've moved forward once. According to the guide, I still need to move forward 2-1=1 more time.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a dense cluster of red bushes on the back-left tile.
There is a group of green pines that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Following the guide, I have moved forward for 2 tiles. However, the guide says I should see a house on the front-right tile, but currently, the front-right tile is just a road. Since the number of tiles in the guide might be inaccurate, I think I should continue moving forward until the scene matches the description exactly.]
Observation: OK.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
There is a group of green pines on the back-right tile.
There is a house on the front-right tile.
The front-left, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now I can see that there are a group of green pines on the back-right tile and a house on the front-right tile, which matches the description in the guide exactly. Therefore I think I can move on to the next step in the guide. I need to turn left to face west. Since I'm currently facing north, turning left once will do it.]
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



nav_construction_obs = """
Important: To help you reach your destination, we've provided a guide. However, it may not always be perfect, as some roads or blocks might be under construction. If that happens, you'll need to find an alternate route and get back on track.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Walk forward (toward east) until you see the destination is on the front-left tile. 
Step 2: Turn left until you are facing north.
Step 3: Walk forward (toward north) until you are close to the destination.

Try your best to navigate to the destination:
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a house that spans the left, back-left tiles.
The front-left, front, back tiles are roads that you can step on.
The front-right, right, back-right tiles are out of the map boundary.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs on the front-left tile, in the front tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house on the back-left tile.
The front, left, back tiles are roads that you can step on.
The front-right, right, back-right tiles are out of the map boundary.
Direction: You are facing east.

Action: think[According to the guide, I should move forward until I see the destination on the front-left tile. However.
The road ahead appears to be under construction, so I need to find an alternative route. It looks like there's a road to my left, so I can turn left here.
Take the first right, and then another right to go around the obstacle.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs on the front-right tile, in the right tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house on the front-left tile.
The front, left, right tiles are roads that you can step on.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs that spans the front-right, right tiles, in the back-right tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house that spans the front-left, left tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs that spans the right, back-right tiles.
There is a house that spans the left, back-left tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the front-right tile.
There is a cluster of orange firs on the back-right tile.
There is a house on the front-left tile.
There is another house on the back-left tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now my right tile is road, according to my plan before, now I can take a right turn.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the front-left tile.
There is a cluster of orange firs on the front-right tile.
There is a house on the back-left tile.
There is another house on the back-right tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs that spans the front-left, left tiles.
There is a cluster of orange firs that spans the front-right, right tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs that spans the left, back-left tiles.
There is a cluster of orange firs that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the back-left tile.
There is a cluster of orange firs on the back-right tile.
There is a dense cluster of red bushes on the front-left tile.
The destination is on the front-right tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: think[Now my right tile is road, according to my plan before, now I can take a right turn again.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the back-right tile.
There is a cluster of orange firs on the front-right tile.
There is a dense cluster of red bushes on the back-left tile.
The destination is on the front-left tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing south.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs that spans the front-right, right tiles.
The destination spans the front-left, left tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
Direction: You are facing south.
Observation: Task completed successfully.
"""



nav_construction_tiles = """
Important: To help you reach your destination, we've provided a guide. However, it may not always be perfect, as some roads or blocks might be under construction. If that happens, you'll need to find an alternate route and get back on track.
Note that you can only move one tile per action and you can only move forward if your front tile is 'road'. If a step in the guide requires you to move multiple tiles, you must execute that number of individual “forward” actions.
For example, if a step requires you to walk five tiles forward, you need to take the “forward” action five times.

Here is one example:
Step-by-Step Guide to Complete the Task:
Start! You are currently facing east.
Step 1. Move forward 5 tiles (east).
Step 2: Turn left until you are facing north.
Step 3: Move forward 1 tile (north) to approach the destination.

Try your best to navigate to the destination:
Observation: You can see the 3x3 tiles surrounding you:
T
There is a house that spans the left, back-left tiles.
The front-left, front, back tiles are roads that you can step on.
The front-right, right, back-right tiles are out of the map boundary.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs on the front-left tile, in the front tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house on the back-left tile.
The front, left, back tiles are roads that you can step on.
The front-right, right, back-right tiles are out of the map boundary.
Direction: You are facing east.

Action: think[According to the guide, I should move forward for 5-1=4 more times. However.
The road ahead appears to be under construction, so I need to find an alternative route. It looks like there's a road to my left, so I can turn left here.
Take the first right turn, and then another right turn to go around the obstacle.]
Observation: OK.

Action: turn left
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs on the front-right tile, in the right tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house on the front-left tile.
The front, left, right tiles are roads that you can step on.
The back-left, back, back-right tiles are out of the map boundary.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs that spans the front-right, right tiles, in the back-right tile there is a pointed construction cone with bold red and white stripes, indicating the road is under construction.
There is a house that spans the front-left, left tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of orange firs that spans the right, back-right tiles.
There is a house that spans the left, back-left tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the front-right tile.
There is a cluster of orange firs on the back-right tile.
There is a house on the front-left tile.
There is another house on the back-left tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing north.

Action: think[Now my right tile is road, according to my plan before, now I can take a right turn.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the front-left tile.
There is a cluster of orange firs on the front-right tile.
There is a house on the back-left tile.
There is another house on the back-right tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs that spans the front-left, left tiles.
There is a cluster of orange firs that spans the front-right, right tiles.
The front, back-left, back, back-right tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs that spans the left, back-left tiles.
There is a cluster of orange firs that spans the right, back-right tiles.
The front-left, front, front-right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: forward
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the back-left tile.
There is a cluster of orange firs on the back-right tile.
There is a dense cluster of red bushes on the front-left tile.
The destination is on the front-right tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing east.

Action: think[Now my right tile is road, according to my plan before, now I can take a right turn again.]
Observation: OK.

Action: turn right
Observation: You can see the 3x3 tiles surrounding you:
Tthere is a cluster of green firs on the back-right tile.
There is a cluster of orange firs on the front-right tile.
There is a dense cluster of red bushes on the back-left tile.
The destination is on the front-left tile.
The front, left, right, back tiles are roads that you can step on.
Direction: You are facing south.

Action: forward
Observation: Task completed successfully.
"""
