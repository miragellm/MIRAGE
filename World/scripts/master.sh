MODEL=qwen3:14b

python main.py --agent_model $MODEL --note rerun --env VillageNav-v0
python main.py --agent_model $MODEL --note rerun --env VillageNav-v0 --manual_type 0
python main.py --agent_model $MODEL --note rerun --env VillageNav-v0 --manual_type 1
python main.py --agent_model $MODEL --note rerun --env VillageNav-v0 --manual_type 2
# ############################################### WRONG ###############################################
# #####################################################################################################
python main.py --agent_model $MODEL --note rerun --env VillageNav-v0 --manual_type 3
python main.py --agent_model $MODEL --note rerun --env VillageNav-v0 --manual_type 4

# ########################################## SEASONAL CHANGES ##########################################
# ######################################################################################################
python main.py --agent_model $MODEL --note rerun --env VillageNav-Seasonal-v0 --manual_type 2

# ############################################ CONSTRUCTION ############################################
# ######################################################################################################
python main.py --agent_model $MODEL --note rerun --env UrbanNav-Construction-v0 --manual_type 0
python main.py --agent_model $MODEL --note rerun --env UrbanNav-Construction-v0 --manual_type 1
python main.py --agent_model $MODEL --note rerun --env UrbanNav-Construction-v0 --manual_type 2

# ############################################### DYNAMIC ###############################################
# #######################################################################################################
python main.py --agent_model $MODEL --note rerun --env VillageNav-Dynamic-v0 --manual_type 0
python main.py --agent_model $MODEL --note rerun --env VillageNav-Dynamic-v0 --manual_type 1
python main.py --agent_model $MODEL --note rerun --env VillageNav-Dynamic-v0 --manual_type 2


python main.py --env Cooking-easy-v0 --manual_type 0 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-v0 --manual_type 1 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-v0 --manual_type 2 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-v0 --manual_type 4 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-crop-gone-v0 --manual_type 2 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-storage-loss-v0 --manual_type 2 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-rookie-chef-v0 --manual_type 2 --seed 1 --agent_model $MODEL
python main.py --env Cooking-multiserve-v0 --manual_type 2 --seed 1 --agent_model $MODEL
python main.py --env Cooking-easy-v0 --seed 1 --agent_model $MODEL


python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 0 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 1 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 2 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 3 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 4 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --manual_type 5 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-shuffle-complex-easy-v0 --manual_type 3 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-rename-easy-v0 --manual_type 3 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-easy-v0 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-shuffle-complex-easy-v0 --manual_type 0 --agent_model $MODEL
python main.py --seed 1 --env Roguelike-rename-easy-v0 --manual_type 0 --agent_model $MODEL
