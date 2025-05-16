# path_converter.py
import re
import random
from ..utils.config import TILE_SIZE
from .utils import change_tile_num, fix_another_usage
from .observation import encode_obs, get_first_person
from pdb import set_trace as st

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def determine_turn(old_direction, new_direction):
    direction_order = [(0, -TILE_SIZE), (TILE_SIZE, 0), (0, TILE_SIZE), (-TILE_SIZE, 0)]    # (up, right, down, left)

    if old_direction not in direction_order or new_direction not in direction_order:
        return None

    old_ind = direction_order.index(old_direction)
    new_ind = direction_order.index(new_direction)
    if (new_ind - old_ind) % 4 == 1:
        return "Turn right"
    elif (new_ind - old_ind) % 4 == 3:
        return "Turn left"
    elif (new_ind - old_ind) % 4 == 2:
        return "Turn around"

    return None

DIRECTION_DICT = {(TILE_SIZE, 0): "east", (0, TILE_SIZE): "south", 
                     (-TILE_SIZE, 0): "west", (0, -TILE_SIZE): "north"}

def convert_path_to_instructions(path,
                                 map_data,
                                 mode,
                                 wrong_tiles=False,
                                 direction='east'):
    # Start! You are currently facing east.
    # Turn right to face south.
    # Move forward 1 tile (south).
    # Move forward 1 tile (west) to approach the destination.
    
    instructions = []
    dir_inverse = {}
    for key, val in DIRECTION_DICT.items():
        dir_inverse[val] = key
    current_direction = dir_inverse[direction]
    tile_count = 0

    instruction_to_steps = []
    curr_steps = ['east', path[0]]
    for i in range(1, len(path)):
        x1, y1 = path[i - 1]
        x2, y2 = path[i]
        dx = x2 - x1
        dy = y2 - y1
        new_direction = (dx, dy)


        if new_direction == current_direction:
            tile_count += 1
        else:
            if tile_count > 0:
                tile = 'tiles' if tile_count != 1 else 'tile'
                instructions.append(f"Move forward {tile_count} {tile} ({DIRECTION_DICT[current_direction]}).")
                instruction_to_steps.append(curr_steps)

            turn_instruction = determine_turn(current_direction, new_direction)
            if turn_instruction:
                instructions.append(f"Turn {turn_instruction} to face {DIRECTION_DICT[new_direction]}.")
                instruction_to_steps.append([])

            current_direction = new_direction
            tile_count = 1
            curr_steps = [DIRECTION_DICT[new_direction], path[i-1]]

        curr_steps.append(path[i])

    # Last movement, all manual steps are correct up to this point 
    if current_direction and tile_count > 0:
        tile = 'tiles' if tile_count != 1 else 'tile'
        instructions.append(f"Move forward {tile_count} {tile} ({DIRECTION_DICT[current_direction]}) to approach the destination.")
        instruction_to_steps.append(curr_steps)

    imperfect_info = [[] for _ in range(len(instructions))]
    if wrong_tiles:
        move_step_indices = [idx for idx, instr in enumerate(instructions) if "Move forward" in instr]
        if len(move_step_indices) > 1:
            move_step_indices = move_step_indices[:-1] # we remove the last step if possible
        n_wrong_tiles = 1 if mode == 'easy' else 3
        # for easy version let's do 1 and for hard version let's do 2 or 3. 
        selected_indices = random.sample(move_step_indices, min(n_wrong_tiles, len(move_step_indices)))
        selected_instructions = [instructions[i] for i in selected_indices]

        for instruction_idx, selected_instruction in zip(selected_indices, selected_instructions):
            modified_instruction = selected_instruction
            match = re.search(r"Move forward (\d+) tile", selected_instruction)
            num_tiles = int(match.group(1))
            if instruction_idx == len(instructions) - 1:
                # corner cases that are actually still correct, for example, when it happens to add an extra tile to the last step
                delta_count, tile_count = change_tile_num(num_tiles, True, ranges=[-1])
            elif num_tiles == 1:
                delta_count, tile_count = change_tile_num(num_tiles, True, ranges=[1]) # can only add steps
            else:
                delta_count, tile_count = change_tile_num(num_tiles, True, ranges=[-1, 1])

            # curr_steps = instruction_to_steps[instruction_idx]
            for season in map_data:
                curr_dir = curr_steps[0]
                imperfect_info[instruction_idx] = [delta_count, curr_steps[-1], curr_dir]
            
            if tile_count <= 1:
                instructions[instruction_idx] = modified_instruction.replace(f"{num_tiles} tiles", f"{tile_count} tile")
            else:
                instructions[instruction_idx] = modified_instruction.replace(str(num_tiles), str(tile_count))

    for i in range(len(instructions)):
        instructions[i] = f'Step {i+1}. {instructions[i]}'

    return instructions, imperfect_info

def get_side_dirs(direction):
    if direction in [(TILE_SIZE, 0), (-TILE_SIZE, 0)]:
        return [(0, TILE_SIZE), (0, -TILE_SIZE)]  # south, north
    else:
        return [(TILE_SIZE, 0), (-TILE_SIZE, 0)]  # east, west

def determine_turn_path(from_dir, to_dir):
    mapping = {
        ((TILE_SIZE, 0), (0, -TILE_SIZE)): "left",
        ((TILE_SIZE, 0), (0, TILE_SIZE)): "right",
        ((-TILE_SIZE, 0), (0, TILE_SIZE)): "left",
        ((-TILE_SIZE, 0), (0, -TILE_SIZE)): "right",
        ((0, TILE_SIZE), (TILE_SIZE, 0)): "left",
        ((0, TILE_SIZE), (-TILE_SIZE, 0)): "right",
        ((0, -TILE_SIZE), (-TILE_SIZE, 0)): "left",
        ((0, -TILE_SIZE), (TILE_SIZE, 0)): "right",
    }
    return mapping.get((from_dir, to_dir), 'unknown')

def count_branches(map_data, path_segment, direction, turn_side):
    side_dirs = get_side_dirs(direction)
    side = side_dirs[0] if turn_side == "left" else side_dirs[1]
    count = 0
    for idx, (x, y) in enumerate(path_segment):
        if idx == 0:
            continue
        sx, sy = x + side[0], y + side[1]
        try:
            if map_data['summer'][sy][sx] == 'road':
                count += 1
        except IndexError:
            continue
    return count

def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def generate_instruction(turn, count, current_dir):
    dir_str = DIRECTION_DICT[current_dir]
    dir_phrase_templates = [
        f"Walk towards {dir_str}",
        f"Head {dir_str}",
        f"Continue going {dir_str}",
    ]
    direction_intro = random.choice(dir_phrase_templates)
    
    main_instruction_templates = [
        f"{direction_intro}, then take the {ordinal(count)} {turn}.",
        f"{direction_intro} and take the {ordinal(count)} {turn}.",
        f"{direction_intro}; turn {turn} at the {ordinal(count)} opportunity.",
    ]
    return random.choice(main_instruction_templates)

def generate_face_instruction(from_dir, to_dir):
    turn = determine_turn_path(from_dir, to_dir)
    if turn == "unknown":
        return f"Turn until you are facing {DIRECTION_DICT[to_dir]}."
    return f"Turn {turn} until you are facing {DIRECTION_DICT[to_dir]}."


def count_intersections_on_final_segment(map_data, path_segment, direction):
    side_dirs = get_side_dirs(direction)
    count = 0
    for idx, (x, y) in enumerate(path_segment):
        if idx == 0:
            continue
        has_left = False
        has_right = False
        for i, side in enumerate(side_dirs):
            sx, sy = x + side[0], y + side[1]
            try:
                if map_data['summer'][sy][sx] == 'road':
                    if i == 0:
                        has_left = True
                    else:
                        has_right = True
            except IndexError:
                continue
        if has_left or has_right:
            count += 1
    return count

def generate_final_instruction(map_data, segment, direction):
    num_intersections = count_intersections_on_final_segment(map_data, segment, direction)

    if num_intersections == 0:
        return "Go straight — your destination is just ahead, before any intersections."
    
    templates = [
        f"Walk straight and pass {num_intersections} intersection{'s' if num_intersections > 1 else ''}, then your destination will be on that stretch.",
        f"Keep walking — after passing {num_intersections} intersection{'s' if num_intersections > 1 else ''}, you'll arrive.",
        f"Continue forward — your goal is right after the {ordinal(num_intersections)} intersection.",
        f"Head straight — the destination is just past the {ordinal(num_intersections)} intersection.",
        f"After you pass {num_intersections} intersection{'s' if num_intersections > 1 else ''}, your destination will be ahead.",
    ]
    return random.choice(templates)


def parse_turn_instruction(selected_instruction):
    # "turn left at the 1st opportunity"
    match = re.search(r"turn (left|right) at the (\d+)(st|nd|rd|th) opportunity", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    # "then take the 1st left"
    match = re.search(r"then take the (\d+)(st|nd|rd|th) (left|right)", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # "and take the 1st left"
    match = re.search(r"and take the (\d+)(st|nd|rd|th) (left|right)", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # "pass N intersections" or "after passing N intersections"
    match = re.search(r"(pass|passing) (\d+) intersection", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    # "after the 1st intersection" / "past the 2nd intersection"
    match = re.search(r"(after|past) the (\d+)(st|nd|rd|th) intersection", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    raise ValueError(f"Cannot parse instruction: {selected_instruction}")

def path_to_turn(path, 
                 map_data, 
                 mode,
                 MAP_ROWS,
                 MAP_COLS,
                 season,
                 start_direction='east',
                 wrong_turns=False):
    
    if wrong_turns:
        include_obs = True
    else:
        include_obs = False
        
    dir_inverse = {v: k for k, v in DIRECTION_DICT.items()}

    current_dir = dir_inverse[start_direction]
    instructions = []
    segment = []

    # --- Initial check: need a turn? ---
    start_idx = 0
    if len(path) >= 2:
        x1, y1 = path[0]
        x2, y2 = path[1]
        first_move = (x2 - x1, y2 - y1)
        if first_move != current_dir:
            instructions.append(generate_face_instruction(current_dir, first_move))
            current_dir = first_move
            start_idx = 1

    # --- Main path ---
    segment = [path[start_idx]]
    for i in range(start_idx+1, len(path)):
        x1, y1 = path[i - 1]
        x2, y2 = path[i]
        move = (x2 - x1, y2 - y1)

        if move == current_dir:
            segment.append((x2, y2))
        else:
            turn = determine_turn_path(current_dir, move)
            if turn in ['left', 'right']:
                branches = count_branches(map_data, segment, current_dir, turn)
                branches = max(1, branches)
                curr_instruction = generate_instruction(turn, branches, current_dir)
                if include_obs:
                    # current observation
                    # print(path[i-1], DIRECTION_DICT[current_dir])
                    obs = get_first_person( (x1, y1),
                                            DIRECTION_DICT[current_dir], 
                                            map_data, 
                                            season, 
                                            MAP_ROWS, 
                                            MAP_COLS, 
                                            TILE_SIZE)
                    encoded_obs = encode_obs(obs,
                                            season)
                    encoded_obs = random.sample(encoded_obs[1:], min(2, len(encoded_obs[1:])))
                    encoded_obs = fix_another_usage(encoded_obs)
                    if len(encoded_obs) == 2:
                        encoded_obs = f"{encoded_obs[0][:-1]} and {encoded_obs[1][:-1]}."
                    else:
                        encoded_obs = ' '.join(encoded_obs)
                        encoded_obs = encoded_obs[:-1] + '.'
                    curr_instruction = curr_instruction+ f" After that, you will see {encoded_obs}"
                instructions.append(curr_instruction)
            else:
                instructions.append(f"Make a turn to face {DIRECTION_DICT[move]}.")
            current_dir = move
            segment = [path[i]]

    if len(segment) >= 1:
        instructions.append(generate_final_instruction(map_data, segment, current_dir))
        
    imperfect_info = []
    if wrong_turns:
        turn_indices = [ idx for idx, instr in enumerate(instructions)
                                if any(phrase in instr for phrase in ["Walk towards", "Head", "Continue going"])]
        # if len(turn_indices) > 1:
        #     turn_indices = turn_indices[:-1] # we remove the last step if possible
        n_wrong_tiles = 1 if mode == 'easy' else 2
        selected_indices = random.sample(turn_indices, min(n_wrong_tiles, len(turn_indices)))
        selected_instructions = [instructions[i] for i in selected_indices]

        for instruction_idx, selected_instruction in zip(selected_indices, selected_instructions):
            modified_instruction = selected_instruction
            num_turns = parse_turn_instruction(selected_instruction)
            if num_turns == 1:
                delta_count, turn_count = change_tile_num(num_turns, True, ranges=[1])
            elif instruction_idx == len(instructions) - 1:
                delta_count, turn_count = change_tile_num(num_turns, True, ranges=[-1])
            else:
                delta_count, turn_count = change_tile_num(num_turns, True, ranges=[-1, 1])
                
            imperfect_info.append(f"At step {instruction_idx+1}, the number of turns is changed by {delta_count}.")
            instructions[instruction_idx] = modified_instruction.replace(ordinal(num_turns), ordinal(turn_count))


    for i in range(len(instructions)):
        if i == 0 and instructions[i].startswith('Continue going'):
            instructions[i] = instructions[i].replace('Continue going', 'Going')
        instructions[i] = f'Step {i+1}. {instructions[i]}'

    return instructions, imperfect_info
