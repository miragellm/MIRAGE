import json
from pdb import set_trace as st
# Path to your .json file
file_path = "config_files/test.json"

# Open and load the JSON file
with open(file_path, "r") as file:
    data = json.load(file)  # Load the JSON data as a Python list

lst = []
# Iterate through the list and find items with "sites": ["reddit"]
for item in data:
    # if "sites" in item and item["sites"] == ["shopping"]:
    # if "sites" in item and item["sites"] == ["gitlab"]:
    if "sites" in item and item["sites"] == ["shopping_admin"]:
        # print(item['intent_template'])
        # print(item['intent'])
        lst.append(item['task_id'])
        # print(item['task_id'])

print(lst)
