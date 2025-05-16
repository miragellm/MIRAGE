cook_react_slightly_mismatched_recipe = """
Here is an example with a similar but not correct recipe:
Unfortunately, we couldn't find the exact recipe the customer requested. However, here is some basic information we can provide about the dish:
- tortilla is grilled
- shrimp is pan-fried
- chicken is pan-fried
- lettuce is raw and chopped
The seasonings should be added during cooking.
In addition, here is a recipe for a similar dish that we hope will be helpful:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw beef x 1 serving, raw scallops x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas.
- pan-fry the raw scallop, raw beef.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
- pan_0, pan_1 are both empty. Capacity: 0/4.
You're not carrying anything right now.

Action: think[Oh no! I don't have the exact recipe. But I have a similar recipe and information about the required dish. Comparing the recipe and the order information, I find that the fillings are different. I don't need the beef and scallop in the recipe, but need the chicken, lettuce and shrimp specified in the order. Therefore, the ingredients I need are tortilla, chicken, lettuce, shrimp and seasonings (cumin, lime juice, olive oil, paprika). I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
- pan_0, pan_1 are both empty. Capacity: 0/4.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. I will generally follow the cooking steps in the similar recipe, and make some modifications according to the ingredient information. The first cooking step is: grill the raw tortillas. According to the information, tortolla is the only grilled ingredient. So no changes are needed. I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw scallop, raw beef. According to the information, the ingredients need to be pan-fried are shrimp and chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are seasonings. Since the required dish has the same flavor as the recipe, no changes are needed for seasonings. In addition, these seasonings are during_cooking, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the grill, pan onto the same plate. Obviously, I need to finish processing all ingredients before this final assembling step. However, I notice that there is still one unprocessed ingredient in my case, which is lettuce. I need to process it first. According to the information, it's raw and chopped. So I will chop it.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished processing all ingredients. I will assemble all the ingredients from the grill, pan onto the same plate. Since I additionally chopped raw lettuce, I should actually assenble from grill_0, pan_0, and cutting_board onto the same plate. I will use plate_0. Next, I will plate from these 3 tools one by one.]
Observation: OK.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of grilled tortilla.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.
pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_crop_gone = """
Here is some other instructions:
1. When you need crops (tomato, carrot, potato, lettuce, cucumber, corn), if you are not told their location, you will prioritize the ones planted in the farm (if any) over those in the store (if any). Because you prefer organic crops.

Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe corn and carrots.However, turkeys have trampled over the lettuce beds. As a result, lettuce cannot be harvested now.
You're not carrying anything right now.

Action: think[Oh no! I cannot harvest lettuce from the farm now. I will buy it in store if they have it.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef; raw lettuce in stock.
You're not carrying anything right now.

Action: think[Great! There is raw lettuce in stock. I will buy lettuce together with other needed ingredients from store: raw chicken, paprika, cumin. I will buy them one by one.]
Observation: OK.

Action: buy raw lettuce
Observation: You successfully bought some raw lettuce.
You have some: raw lettuce with you.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: plate from pan_0 into plate_0
Observation: pan_0 is still cooking. Wait until the food is ready before plating.

Action: think[pan_0 hasn't finished cooking. I will wait for a timestep, and then try to plate it again.]
Observation: OK.

Action: wait
Observation: 1 timestep has passed.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_storage_loss = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Let's begin. You need to cook these 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
- pan_0, pan_1 are both empty. Capacity: 0/4.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
- pan_0, pan_1 are both empty. Capacity: 0/4.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: You put paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_0
Observation: You put cumin into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_0
Observation: Oops! you reach for the lime juice, but the containers are already empty, so your action couldn't be completed.

Action: think[Oh no! I have no lime juice now. I will go out to the store to buy some and come back to the restaurant to continue cooking the dish.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef; lime juice in stock.
You're not carrying anything right now.

Action: buy lime juice
Observation: You successfully bought some lime juice.
pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.
You have some: lime juice with you.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the cabinet with lime juice. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; paprika; cumin; lime juice.
There are 5 cooking tools in the environment:
- grill_1 is empty. Capacity: 0/1.
- pan_1 is empty. Capacity: 0/4.
- cutting_board holds raw, chopped lettuce. Capacity: 1/1.
- grill_0 holds grilled tortillas, no seasonings. Capacity: 1/1.
- pan_0 holds pan-fried shrimps, pan-fried chicken, with seasonings: olive oil, paprika, cumin. Capacity: 2/4.
You're not carrying anything right now.

Action: put lime juice into pan_0
Observation: You put lime juice into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[Now I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_0 finished baking. I will first plate from cutting_board and grill_0, and finally pan_0, and then wait until pan_0 finishes cooking.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: wait
Observation: pan_0 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: plate from pan_0 into plate_0
Observation: You plated all cooked ingredients from pan_0 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""

cook_react_rookie_chef = """
Here is one example with recipe:
recipe for 1 serving of **taco (Smoky Lime)**
### Ingredients:
raw chicken x 1 serving, raw lettuce x 1 serving, raw shrimps x 1 serving, raw tortillas x 1 serving.
### Seasonings:
Add during cooking: cumin, lime juice, olive oil, paprika.
### Cooking Steps:
- grill the raw tortillas; then chop the raw lettuce.
- pan-fry the raw shrimp, raw chicken.
- add olive oil, paprika, cumin, lime juice on the pan.
- wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate.
### You'll need to collect ingredients from the following locations:
**Farm**: lettuce
**Harbor_2**: shrimp
**Store**: chicken, cumin, paprika

Observation: Incoming order! Please make 1 dishes: 1 serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas.
In the cabinet, you see: olive oil; lime juice.
There are 5 cooking tools in the environment:
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
- pan_0, pan_1 are both empty. Capacity: 0/4.
You're not carrying anything right now.

Action: think[First, I need to gather all the ingredients. I already have tortillas, olive oil, lime juice in the kitchen. I still need lettuce, shrimp, chicken, cumin, paprika. I am told the locations of these needed ingredients: lettuce at the farm, shrimp at the harbor_2, and chicken, cumin, paprika at the store. I will visit these locations one by one to get these ingredients. First, I will go to the farm for lettuce.]
Observation: OK.

Action: goto farm
Observation: You are at the farm. In the farm, you see ripe lettuce, corn, and carrots.
You're not carrying anything right now.

Action: think[I will harvest the lettuce.]
Observation: OK.

Action: harvest lettuce
Observation: You harvested all the lettuce!
You have some: raw lettuce with you.

Action: think[I now have the lettuce. Next, I will go to the store to get chicken, cumin, paprika.]
Observation: OK.

Action: goto store
Observation: In the store, you see raw chicken; paprika; cumin; raw flour; raw peas; raw scallops; raw rice; raw beef in stock.
You have some: raw lettuce with you.

Action: think[I will buy raw chicken, paprika, cumin one by one.]
Observation: OK.

Action: buy raw chicken
Observation: You successfully bought some raw chicken.
You have some: raw lettuce, raw chicken with you.

Action: buy paprika
Observation: You successfully bought some paprika.
You have some: raw lettuce, raw chicken, paprika with you.

Action: buy cumin
Observation: You successfully bought some cumin.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I now have raw chicken, paprika. cumin. Next, I will go to the harbor_2 to get shrimps.]
Observation: OK.

Action: goto harbor_2
Observation: You walk to harbor_2. The spot is free, and you can get ready to fish here.
You have some: raw lettuce, raw chicken, paprika, cumin with you.

Action: think[I can fish at harbor_2. I will start fishing the seafood I need, which is shrimp.]
Observation: OK.

Action: fish shrimp
Observation: You pulled up some scallops instead.

Action: think[I got a wrong kind of seafood. I still need to fish shrimp. I will try again.]
Observation: OK.

Action: fish shrimp
Observation: You reeled in some fresh shrimps!
You have some: raw lettuce, raw chicken, paprika, cumin, raw shrimps with you.

Action: think[I successfully got raw shrimps. Now I have all the ingredients I need. I can go back to the restaurant to cook the dish.]
Observation: OK.

Action: goto restaurant
Observation: You are now in the kitchen of your restaurant. You restock the fridge with raw lettuce; raw chicken; raw shrimps. 
You restock the cabinet with paprika; cumin. 
You are now in the kitchen of your restaurant.
In the fridge, you see: raw tortillas; raw lettuce; raw chicken; raw shrimps.
In the cabinet, you see: olive oil; lime juice; paprika; cumin.
There are 5 cooking tools in the environment:
- pan_0, pan_1 are both empty. Capacity: 0/4.
- cutting_board, grill_0, grill_1 are all empty. Capacity: 0/1.
You're not carrying anything right now.

Action: think[Now I'm at restaurant, ready to cook. The first cooking step is: grill the tortillas; then chop the lettuce. First, I will put the raw tortilla into grill_0 to grill it.]
Observation: OK.

Action: put raw tortillas into grill_0
Observation: You put raw tortilla into the grill_0. Please wait for 2 timesteps for it to be cooked.

Action: think[Next I will complete the second half of cooking step 1 is to chop the lettuce.]
Observation: OK.

Action: chop raw lettuce
Observation: You chopped the lettuce on the cutting board. cutting board now holds: raw,chopped lettuce.

Action: think[Now I have finished cooking step 1. I will continue with cooking step 2: pan-fry the raw shrimp, raw chicken. I will put them into pan_0 one by one to pan-fry them.]
Observation: OK.

Action: put raw shrimps into pan_0
Observation: You put raw shrimp into the pan_0. Please wait for 3 timesteps for it to be cooked.
grill_0 finished cooking your one serving of grilled tortilla.

Action: put raw chicken into pan_0
Observation: You put raw chicken into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 2. I will move to cooking step 3: add olive oil, paprika, cumin, lime juice on the pan. These are all during_cooking seasonings, so I can add them now (despite that pan_0 hasn't finished cooking). I will put them into pan_0 one by one.]
Observation: OK.

Action: put olive oil into pan_0
Observation: You put olive oil into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_0
Observation: Oops! You accidentally added an extra serving of paprika.You put 2 servings of paprika into the pan_0. Please wait for 3 timesteps for it to be cooked.

Action: think[Oh no! I put extra paprika. I have to re-cook all ingredients in pan_0. I will use pan_1 to re-cook them.]

Action: put raw shrimps into pan_1
Observation: You put raw shrimp into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: put raw chicken into pan_1
Observation: You put raw chicken into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: put olive oil into pan_1
Observation: You put olive oil into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: put paprika into pan_1
Observation: You put paprika into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: put cumin into pan_1
Observation: You put cumin into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: put lime juice into pan_1
Observation: You put lime juice into the pan_1. Please wait for 3 timesteps for it to be cooked.

Action: think[I have finished cooking step 3. I will move to cooking step 4: wait for all ingredients to finish cooking, then assemble all the ingredients from the cutting_board, grill, pan onto the same plate. I will use plate_0. According to the latest observation, I need to wait 3 timesteps until pan_1 finished baking. I will first plate from cutting_board and grill_0, and wait until pan_1 finishes cooking before plate pan_1.]
Observation: OK.

Action: plate from cutting_board into plate_0
Observation: You plated all cooked ingredients from cutting_board into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning.

Action: plate from grill_0 into plate_0
Observation: You plated all cooked ingredients from grill_0 into plate_0. plate_0: a plated dish with 1 serving of raw, chopped lettuce without any seasoning; 1 serving of grilled tortilla without any seasoning.

Action: wait
Observation: pan_1 finished cooking your one serving of pan-fried chicken, pan-fried shrimp.

Action: plate from pan_1 into plate_0
Observation: You plated all cooked ingredients from pan_1 into plate_0. plate_0: A successfully prepared serving of the requested **taco (Smoky Lime)**.

Action: think[plate_0 is now filled with one serving of completed **taco (Smoky Lime)**. I can serve plate_0 now.]
Observation: OK.

Action: serve plate_0
Observation: Successfully served plate_0. This is a successful serving of **taco (Smoky Lime)**, filled with chicken, lettuce, and shrimps.
"""
