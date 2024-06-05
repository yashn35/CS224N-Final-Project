import os
import json
import numpy as np
from openai import OpenAI
import ast

# Set up OpenAI API key

client = OpenAI(
    # This is the default and can be omitted
    # api_key=""
)

# Define the 15 items for the desert survival challenge
items = [
    "Torch with 4 battery-cells", "Folding knife", "Air map of the area", "Plastic raincoat (large size)", "Magnetic compass",
    "First-aid kit", "45 calibre pistol (loaded)", "Parachute (red & white)", "Bottle of 1000 salt tablets",
    "2 litres of water per person", "A book entitled 'Desert Animals That Can Be Eaten'", "Sunglasses (for everyone)",
    "2 litres of 180 proof liquor", "Overcoat (for everyone)", "A cosmetic mirror"
]


PROMPT = """
It is approximately 10:00 am in mid-July and you have just crash landed in the Atacama Desert in South America. Your light twin-engined plane containing the bodies of the pilot and co-pilot has completely burned out with only the frame remaining. None of you have been injured.

The pilot was unable to notify anyone of your position before the crash. However, he had indicated before impact that you were 50 miles from a mining camp, which is the nearest known settlement, and approximately 65 miles off the course that was filed in your Flight Plan. The immediate area is quite flat, except for occasional cacti, and appears to be rather barren. The last weather report indicated that the temperature would reach 110 F today, which means that the temperature at ground level will be 130 F.

You are dressed in lightweight clothing-short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

Before your plane caught fire, your group was able to salvage the 15 items listed on the
“Salvaged Items” page. Your task is to rank these items according to their importance to your survival, starting with a “1” for the most important, to a “15” for the least important.

Torch with 4 battery-cells [RANKING]
Folding knife [RANKING]
Air map of the area [RANKING]
Plastic raincoat (large size) [RANKING]
Magnetic compass [RANKING]
First-aid kit [RANKING]
45 calibre pistol (loaded) [RANKING]
Parachute (red & white) [RANKING]
Bottle of 1000 salt tablets [RANKING]
2 litres of water per person [RANKING]
A book entitled 'Desert Animals That Can Be Eaten' [RANKING]
Sunglasses (for everyone) [RANKING]
2 litres of 180 proof liquor [RANKING]
Overcoat (for everyone) [RANKING]
A cosmetic mirror [RANKING]

OUTPUT THE RANKINGS AS A DICTIONARY OF EACH ITEM WITH THE ITEM AND ITS CORRESPONDING RANKING. EACH RANKING MUST BE AN INTEGER BETWEEN 1 AND 15 INCLUSIVE AND EACH NUMBER MUST SHOW UP EXACTLY ONCE. DO NOT INCLUDE ANY MISCELLANEOUS INFORMATION. ONLY OUTPUT A DICTIONARY.
"""


agents = [
    {"name": "Alice", "gender": "female", "persona": "a resourceful survival expert"},
    {"name": "Bob", "gender": "male", "persona": "a practical and logical thinker"},
    {"name": "Charlie", "gender": "male", "persona": "an adventurous and risk-taking individual"},
    {"name": "Daisy", "gender": "female", "persona": "a cautious and detail-oriented planner"},
    {"name": "Eve", "gender": "female", "persona": "a creative and imaginative problem-solver"},
    {"name": "Frank", "gender": "male", "persona": "a no-nonsense pragmatist"},
    {"name": "Grace", "gender": "female", "persona": "a calm and collected decision-maker"},
    {"name": "Hank", "gender": "male", "persona": "a strategic and analytical thinker"},
    {"name": "Ivy", "gender": "female", "persona": "an empathetic and cooperative team player"},
    {"name": "Jack", "gender": "male", "persona": "a curious and open-minded explorer"}
]

output_folder = "rankings"
interaction_folder = "interactions"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(interaction_folder, exist_ok=True)


def load_rankings(agent_names, path, t):
    rankings = {}
    for agent in agent_names:
        filename = os.path.join(path, f"{agent}/t{t}{agent}.json")
        with open(filename, "r") as f:
            rankings[agent] = json.load(f)
    return rankings


def load_votes_explanations(agent_names, path, t, i, rank):
    votes = {}
    for agent in agent_names:
        filename = os.path.join(path, f"{agent}/t{t}r{rank}{agent}_{i}.json")
        with open(filename, "r") as f:
            votes[agent] = json.load(f)
        f.close()
    return votes



def check_converge(items_explanations, key):
    """
    :param rankings_explanations: dict of dicts. {agent_name: {key, 'explanation'}}
    :return: True if all agents in rankings_explanations have the same preferred ranking. False otherwise
    """
    chosen_names = [agent[key] for agent in items_explanations.values()]
    return chosen_names[1:] == chosen_names[:-1]


# TODO: Update for trials and stuff
def save_interaction(agent_name, interaction, step, type):
    with open(os.path.join(interaction_folder, f"{agent_name}_{type}_{step}.json"), "w") as f:
        json.dump(interaction, f, indent=4)


def remind_and_vote(agent, rankings, path_to_save, verbose=False, debug=False):
    """

    :param agent: persona we want the model to take on. A dict from the agents list
    :param rankings: all the rankings as a list
    :param path_to_save: path of dumped json
    :return: the ranking the model voted for (string)
    """
    voting_prompt = f"""
    It is approximately 10:00 am in mid-July and you have just crash landed in the Atacama Desert in South America. Your light twin-engined plane containing the bodies of the pilot and co-pilot has completely burned out with only the frame remaining. None of you have been injured.

    The pilot was unable to notify anyone of your position before the crash. However, he had indicated before impact that you were 50 miles from a mining camp, which is the nearest known settlement, and approximately 65 miles off the course that was filed in your Flight Plan. The immediate area is quite flat, except for occasional cacti, and appears to be rather barren. The last weather report indicated that the temperature would reach 110 F today, which means that the temperature at ground level will be 130 F.

    You are dressed in lightweight clothing-short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

    Before your plane caught fire, your group was able to salvage the 15 items listed below.
    
    Torch with 4 battery-cells [RANKING]
    Folding knife [RANKING]
    Air map of the area [RANKING]
    Plastic raincoat (large size) [RANKING]
    Magnetic compass [RANKING]
    First-aid kit [RANKING]
    45 calibre pistol (loaded) [RANKING]
    Parachute (red & white) [RANKING]
    Bottle of 1000 salt tablets [RANKING]
    2 litres of water per person [RANKING]
    A book entitled 'Desert Animals That Can Be Eaten' [RANKING]
    Sunglasses (for everyone) [RANKING]
    2 litres of 180 proof liquor [RANKING]
    Overcoat (for everyone) [RANKING]
    A cosmetic mirror [RANKING]
    
    The other survivors have ranked these items according to their importance to your survival, starting with a “1” for the most important, to a “15” for the least important.
    
    Your task is to pick the ranking that you think is the best out of the ten rankings listed below. Output the entire ranking that you think is the best as well as the name of the person who made that ranking and a five sentence explanation why you picked that ranking.
    
    Alice's ranking: {rankings['Alice']}
    
    Bob's ranking: {rankings['Bob']}
    
    Charlie's ranking: {rankings['Charlie']}
    
    Daisy's ranking: {rankings['Daisy']}
    
    Eve's ranking: {rankings['Eve']}
    
    Frank's ranking: {rankings['Frank']}
    
    Grace's ranking: {rankings['Grace']}
    
    Hank's ranking: {rankings['Hank']}
    
    Ivy's ranking: {rankings['Ivy']}
    
    Jack's ranking: {rankings['Jack']}
    
    YOUR OUTPUT:
    'name': name of person who made the best ranking,
    'ranking': the best ranking as a python dict,
    'explanation': five sentence explanation of why that ranking is the best
    """

    if debug:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4o"
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": f"You are {agent['name']}. You are {agent['persona']} who outputs JSON"},
            {"role": "user", "content": voting_prompt}
        ],
        max_tokens=600
    )
    content = response.choices[0].message.content.strip()
    # Clean the response content
    if content.startswith("```") and content.endswith("```"):
        feedback_content = content[3:-3].strip()

    if verbose:
        print(content)
        print(f"This from agent {agent['name']}")

    try:
        rankings_dict = ast.literal_eval(content)
    except:
        print("Error occurred trying to convert to dict")
        rankings_dict = {}

    with open(path_to_save, 'w') as f:
        json.dump(rankings_dict, f, indent=4)


def consider_feedback_and_vote(agent, rankings, path_to_save, verbose=False, debug=False):
    """
        :param agent: persona we want the model to take on. A dict from the agents list
        :param rankings: all the rankings as a list
        :param path_to_save: path of dumped json
        :return: the ranking the model voted for (string)
        """
    voting_prompt = f"""
        It is approximately 10:00 am in mid-July and you have just crash landed in the Atacama Desert in South America. Your light twin-engined plane containing the bodies of the pilot and co-pilot has completely burned out with only the frame remaining. None of you have been injured.

        The pilot was unable to notify anyone of your position before the crash. However, he had indicated before impact that you were 50 miles from a mining camp, which is the nearest known settlement, and approximately 65 miles off the course that was filed in your Flight Plan. The immediate area is quite flat, except for occasional cacti, and appears to be rather barren. The last weather report indicated that the temperature would reach 110 F today, which means that the temperature at ground level will be 130 F.

        You are dressed in lightweight clothing-short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

        Before your plane caught fire, your group was able to salvage the 15 items listed below.

        Torch with 4 battery-cells [RANKING]
        Folding knife [RANKING]
        Air map of the area [RANKING]
        Plastic raincoat (large size) [RANKING]
        Magnetic compass [RANKING]
        First-aid kit [RANKING]
        45 calibre pistol (loaded) [RANKING]
        Parachute (red & white) [RANKING]
        Bottle of 1000 salt tablets [RANKING]
        2 litres of water per person [RANKING]
        A book entitled 'Desert Animals That Can Be Eaten' [RANKING]
        Sunglasses (for everyone) [RANKING]
        2 litres of 180 proof liquor [RANKING]
        Overcoat (for everyone) [RANKING]
        A cosmetic mirror [RANKING]

        The other survivors have ranked these items according to their importance to your survival, starting with a “1” for the most important, to a “15” for the least important.
        They have also provided an explanation to their ranking.

        Your task is to pick the ranking that you think is the best out of the ten rankings listed below. Carefully consider the explanations for each ranking and pick one.
        Output the entire ranking that you think is the best as well as the name of the person who made that ranking and a five sentence explanation why you picked that ranking.

        Alice's ranking: {rankings['Alice']['ranking']}
        Alice's explanation: {rankings['Alice']['explanation']}

        Bob's ranking: {rankings['Bob']['ranking']}
        Bob's explanation: {rankings['Bob']['explanation']}

        Charlie's ranking: {rankings['Charlie']['ranking']}
        Charlie's explanation: {rankings['Charlie']['explanation']}

        Daisy's ranking: {rankings['Daisy']['ranking']}
        Daisy's explanation: {rankings['Daisy']['explanation']}

        Eve's ranking: {rankings['Eve']['ranking']}
        Eve's explanation: {rankings['Eve']['explanation']}

        Frank's ranking: {rankings['Frank']['ranking']}
        Frank's explanation: {rankings['Frank']['explanation']}

        Grace's ranking: {rankings['Grace']['ranking']}
        Grace's explanation: {rankings['Grace']['explanation']}

        Hank's ranking: {rankings['Hank']['ranking']}
        Hank's explanation: {rankings['Hank']['explanation']}

        Ivy's ranking: {rankings['Ivy']['ranking']}
        Ivy's explanation: {rankings['Ivy']['explanation']}

        Jack's ranking: {rankings['Jack']['ranking']}
        Jack's explanation: {rankings['Jack']['explanation']}

        YOUR OUTPUT:
        'name': name of person who made the best ranking,
        'ranking': the best ranking as a python dict,
        'explanation': five sentence explanation of why that ranking is the best
        """
    if debug:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4o"
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": f"You are {agent['name']}. You are {agent['persona']} who outputs JSON."},
            {"role": "user", "content": voting_prompt}
        ],
        max_tokens=600
    )
    content = response.choices[0].message.content.strip()
    # Clean the response content
    if content.startswith("```") and content.endswith("```"):
        feedback_content = content[3:-3].strip()

    if verbose:
        print(content)
        print(f"This from agent {agent['name']}")

    try:
        rankings_dict = ast.literal_eval(content)
    except:
        print("Error occurred trying to convert to dict")
        rankings_dict = {}

    with open(path_to_save, 'w') as f:
        json.dump(rankings_dict, f, indent=4)


def get_agent_obj(agent_name):
    for agent_obj in agents:
        if agent_obj['name'] == agent_name:
            return agent_obj
    return ""


# TODO maybe record number of iterations to converge
def run_democracy(path_to_rankings, agent_names, trials=5, max_interacts=0, verbose=False):
    """
    Vote on which ranking is the best.
        1. Load individual rankings for the trial
        2. Prompt each agent to vote on the ranking they like the most
            2a) Prompt each agent to explain why they like that one the most
            2b) Give each agent the reasons from all the other agents and ask to vote again
            2c) Repeat 2a and 2b until max level of interactions is reached or agents converge
        3. The ranking that gets the most votes is selected as the group ranking
    :param:
        verbose: print outputs and reasoning if true. saves to file if false
        agent_names: list of agent names
    :return: group ranking
    """
    all_rankings_over_trials = []
    for trial in range(1, trials+1):
        all_rankings = load_rankings(agent_names, path_to_rankings, trial)
        all_rankings_over_trials.append(all_rankings)
        print(f'Done loading rankings for trial {trial}')
        for agent in agent_names:
            print(f"Starting {agent}'s vote.")
            path_to_save = f"interactions/democracy/{agent}"
            if not os.path.isdir(path_to_save):
                os.mkdir(path_to_save)
            path_to_save = os.path.join(path_to_save, f't{trial}{agent}_0.json')
            # Remind model of their persona and inform the model of all the rankings.
            # Prompt model to vote and explain why the like the one they chose
            remind_and_vote(get_agent_obj(agent), all_rankings, path_to_save, verbose)
            print(f"Wrote to {path_to_save}\n---------------------------")

        print(f"---------------------------\nDone with initial vote.")
        print(f"Beginning interactions. Max interaction level: {max_interacts}")
        for i in range(max_interacts):
            print(f'Starting interaction level {i + 1}')
            path_to_rankings_explanations = "interactions/democracy"
            print(f'Loading interactions from level {i}')
            rankings_and_explanations = load_votes_explanations(agent_names, path_to_rankings_explanations,
                                                                trial, i)
            # If models all agree, just break early
            if check_converge(rankings_and_explanations, "ranking"):
                print(f"YAY EVERYONE AGREES")
                break
            for agent in agent_names:
                # Provide model with the reasoning and votes of the other models
                path_to_save = f"interactions/{agent}"
                if not os.path.isdir(path_to_save):
                    os.mkdir(path_to_save)
                path_to_save = os.path.join(path_to_save, f't{trial}{agent}_{i+1}.json')
                consider_feedback_and_vote(get_agent_obj(agent), rankings_and_explanations,
                                           path_to_save, verbose)
                print(f"Wrote to {path_to_save}\n---------------------------")


#agent_names = [a['name'] for a in agents]
#run_democracy("rankings", agent_names, trials=5, max_interacts=2, verbose=True)


def get_most_important_item(agent, remain_items, path_to_save, verbose=False, debug=False):
    """
        :param agent: persona we want the model to take on. A dict from the agents list
        :param remain_items: remaining items left to rank (list)
        :param path_to_save: path of dumped json
        :return: the ranking the model voted for (string)
        """
    voting_prompt = f"""
        It is approximately 10:00 am in mid-July and you have just crash landed in the Atacama Desert in South America. Your light twin-engined plane containing the bodies of the pilot and co-pilot has completely burned out with only the frame remaining. None of you have been injured.

        The pilot was unable to notify anyone of your position before the crash. However, he had indicated before impact that you were 50 miles from a mining camp, which is the nearest known settlement, and approximately 65 miles off the course that was filed in your Flight Plan. The immediate area is quite flat, except for occasional cacti, and appears to be rather barren. The last weather report indicated that the temperature would reach 110 F today, which means that the temperature at ground level will be 130 F.

        You are dressed in lightweight clothing-short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

        Before your plane caught fire, your group was able to salvage some items.
        
        These are the remaining items that need to be ranked:
        remaining_items: {remain_items}

        Your task is to pick the remaining item that you think is the most important out of the remaining_items list.
        Output the item you think is the most important to your collective survival out of the items in the remaining_items list.
        Also output a three sentence explanation of why you picked that item.

        YOUR OUTPUT:
        'item': the most important item from the remaining_items list,
        'explanation': three sentence explanation of why that item is the most important
        """
    if debug:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4o"
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": f"You are {agent['name']}. You are {agent['persona']} who outputs JSON."},
            {"role": "user", "content": voting_prompt}
        ],
        max_tokens=600
    )
    content = response.choices[0].message.content.strip()
    # Clean the response content
    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3].strip()

    if verbose:
        print(content)
        print(f"This from agent {agent['name']}")

    try:
        choice_dict = ast.literal_eval(content)
    except:
        print("Error occurred trying to convert to dict")
        choice_dict = {}

    with open(path_to_save, 'w') as f:
        json.dump(choice_dict, f, indent=4)


def consider_and_get_most_important_remaining_item(agent, ranking_so_far, remain_items, choices, path_to_save, verbose=False, debug=False):
    """
        :param agent: persona we want the model to take on. A dict from the agents list
        :param ranking_so_far: the ranking so far
        :param remain_items: remaining items left to rank (list)
        :param choices: dict of choices and explanations by the all agents
        :param path_to_save: path of dumped json
        :return: the ranking the model voted for (string)
        """
    voting_prompt = f"""
        It is approximately 10:00 am in mid-July and you have just crash landed in the Atacama Desert in South America. Your light twin-engined plane containing the bodies of the pilot and co-pilot has completely burned out with only the frame remaining. None of you have been injured.

        The pilot was unable to notify anyone of your position before the crash. However, he had indicated before impact that you were 50 miles from a mining camp, which is the nearest known settlement, and approximately 65 miles off the course that was filed in your Flight Plan. The immediate area is quite flat, except for occasional cacti, and appears to be rather barren. The last weather report indicated that the temperature would reach 110 F today, which means that the temperature at ground level will be 130 F.

        You are dressed in lightweight clothing-short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

        Before your plane caught fire, your group was able to salvage some items.
        
        The group has already ranked the following items:
        ranking_so_far: {ranking_so_far}
        
        These are the remaining items that need to be ranked:
        remaining_items: {remain_items}

        Your task is to pick the remaining item that you think is the most important out of the remaining_items list.
        Carefully consider the following explanations provided by your teammates before making your decision.
        Output the item you think is the most important to your collective survival out of the items in the remaining_items list.
        Also output a three sentence explanation of why you picked that item.
        
        Alice's choice: {choices['Alice']['item']}
        Alice's explanation: {choices['Alice']['explanation']}

        Bob's choice: {choices['Bob']['item']}
        Bob's explanation: {choices['Bob']['explanation']}

        Charlie's choice: {choices['Charlie']['item']}
        Charlie's explanation: {choices['Charlie']['explanation']}

        Daisy's choice: {choices['Daisy']['item']}
        Daisy's explanation: {choices['Daisy']['explanation']}

        Eve's choice: {choices['Eve']['item']}
        Eve's explanation: {choices['Eve']['explanation']}

        Frank's choice: {choices['Frank']['item']}
        Frank's explanation: {choices['Frank']['explanation']}

        Grace's choice: {choices['Grace']['item']}
        Grace's explanation: {choices['Grace']['explanation']}

        Hank's choice: {choices['Hank']['item']}
        Hank's explanation: {choices['Hank']['explanation']}

        Ivy's choice: {choices['Ivy']['item']}
        Ivy's explanation: {choices['Ivy']['explanation']}

        Jack's choice: {choices['Jack']['item']}
        Jack's explanation: {choices['Jack']['explanation']}

        YOUR OUTPUT:
        'item': the most important item from the remaining_items list,
        'explanation': three sentence explanation of why that item is the most important
        """
    if debug:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4o"
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": f"You are {agent['name']}. You are {agent['persona']} who outputs JSON."},
            {"role": "user", "content": voting_prompt}
        ],
        max_tokens=600
    )
    content = response.choices[0].message.content.strip()
    # Clean the response content
    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3].strip()

    if verbose:
        print(content)
        print(f"This from agent {agent['name']}")

    try:
        rankings_dict = ast.literal_eval(content)
    except:
        print("Error occurred trying to convert to dict")
        rankings_dict = {}

    with open(path_to_save, 'w') as f:
        json.dump(rankings_dict, f, indent=4)
    f.close()


def count_votes(path_to_load, agent_names, trial, i, key, current_rank, verbose=False):
    """
    Counts votes and removes most voted item from input list
    :param path_to_load: path to directory containing all votes
    :return: most popular item
    """
    votes = {}
    for agent in agent_names:
        filename = os.path.join(path_to_load, f"{agent}/t{trial}r{current_rank}{agent}_{i}.json")
        with open(filename, 'r') as f:
            loaded_dict = json.load(f)
            vote = loaded_dict[key]
            if vote not in votes.keys():
                votes[vote] = 0
            votes[vote] += 1
        f.close()
    with open(os.path.join(path_to_load, f"votes/t{trial}r{current_rank}votes_{i}.json"), 'w') as f:
        json.dump(votes, f, indent=4)
    f.close()
    if verbose:
        print(f"Final votes: \n {votes}")
    return max(votes, key=votes.get)


def run_one_by_one(path_to_rankings, agent_names, trials=5, max_interacts=1, verbose=False, debug=False):
    """
    Vote on which item should be first, then second, then third, etc.
        1. Load individual rankings for the trial
        2. Prompt each agent to vote on which item they think is the most important
            2a) Prompt each agent to explain why they think that item is the most important
            2b) Give each agent the reasons from all the other agents and ask to vote again
            2c) Repeat 2a and 2b until max level of interactions is reached or agents converge
        3. Repeat step 2 until all items have been ranked and return the group ranking
    :param:
        verbose: print outputs and reasoning if true. saves to file if false
        agent_names: list of agent names
    :return: group ranking
    """
    all_rankings_over_trials = []
    for trial in range(1, trials + 1):
        print(f'Done loading individual rankings for trial {trial}')
        remaining_items = items.copy()
        #all_rankings = load_rankings(agent_names, path_to_rankings, trial)
        #all_rankings_over_trials.append(all_rankings)
        ranking_so_far = {}
        current_rank = 1
        while len(remaining_items) > 0 and current_rank <= len(items):
            print(f"Remaining items are {remaining_items}")
            print(f"Current ranking is {ranking_so_far}")
            print(f"Deciding for rank {current_rank}")

            for agent in agent_names:
                print(f"Starting {agent}'s initial vote.")
                path_to_save = f"interactions/one_by_one/{agent}"
                if not os.path.isdir(path_to_save):
                    os.mkdir(path_to_save)
                path_to_save = os.path.join(path_to_save, f't{trial}r{current_rank}{agent}_0.json')
                # Remind model of their persona and inform the model of all the rankings.
                # Prompt model to vote and explain why the like the one they chose
                get_most_important_item(get_agent_obj(agent), remaining_items, path_to_save, verbose=verbose, debug=debug)
                print(f"Wrote to {path_to_save}\n---------------------------")

            print(f"Done with initial vote.\n---------------------------")
            print(f"Beginning interactions. Max interaction level: {max_interacts}")
            last_i = 0
            for i in range(max_interacts):
                last_i = i
                print(f'Starting interaction level {i + 1}')
                path_to_choices_explanations = "interactions/one_by_one"
                print(f'Loading interactions from level {i}')
                choices_and_explanations = load_votes_explanations(agent_names, path_to_choices_explanations, trial, i,
                                                                   current_rank)
                # If models all agree, just break early
                if check_converge(choices_and_explanations, "item"):
                    print(f"YAY EVERYONE AGREES")
                    break
                for agent in agent_names:
                    # Provide model with the reasoning and votes of the other models
                    path_to_save = f"interactions/one_by_one/{agent}"
                    if not os.path.isdir(path_to_save):
                        os.mkdir(path_to_save)
                    path_to_save = os.path.join(path_to_save, f't{trial}r{current_rank}{agent}_{i + 1}.json')
                    consider_and_get_most_important_remaining_item(get_agent_obj(agent), ranking_so_far,
                                                                   remaining_items, choices_and_explanations,
                                                                   path_to_save, verbose=verbose, debug=debug)
                    print(f"Wrote to {path_to_save}")

            # Talley votes at maximum level of interaction
            voted_item = count_votes("interactions/one_by_one", agent_names, trial,
                                     last_i, key="item", current_rank=current_rank)
            try:
                remaining_items.remove(voted_item)
            except:
                print(f"Error removing {voted_item} from list")
            ranking_so_far[voted_item] = current_rank
            print(f"Done with rank {current_rank}")
            print(f"-------------------------------\n-------------------------------")
            current_rank += 1

        path_to_result = os.path.join("interactions/one_by_one")
        with open(os.path.join(path_to_result, f"t{trial}group_ranking.json"), 'w') as f:
            json.dump(ranking_so_far, f, indent=4)
        f.close()
        print(f"-------------------------------\n-------------------------------")
        print(f"Done with trial {trial}")
        print(f"-------------------------------\n-------------------------------")


agent_names = [a['name'] for a in agents]
run_one_by_one("rankings", agent_names, trials=5, max_interacts=1, verbose=True, debug=False)


def run_dictatorship(path_to_rankings, agent_names, trials=5, max_interacts=1, verbose=False):
    """
    A randomly selected dictator considers all rankings and reasoning and decides the best ranking
        1. Load individual rankings for the trial
        2. Randomly choose a dictator agent
        2. The dictator poses the question of why each agent made their ranking
            2a) Prompt each agent to answer the dictator's question
            2b) The dictator considers all the answers and can either ask a question or pick a ranking
            2c) Repeat 2a and 2b until max level of interactions is reached or the dictator picks a ranking
        3. The ranking the dictator picked is chosen to be the group's ranking
    :param:
        verbose: print outputs and reasoning if true. saves to file if false
        agent_names: list of agent names
    :return: group ranking
    """



# ------ DEPRECATED ------
def simulate_discussion(rankings):
    for step in range(1):  # Rounds of discussion, that is feedback back and forth
        step_feedback = {}
        
        # Collect feedback from all agents for each agent
        for agent in agents:
            print(f"Current agent: {agent}")
            feedback_prompt = f"Your peer agent {agent['name']} has the following individual ranking: {rankings[agent['name']]}. Provide your feedback on {agent['name']}'s rankings based on your own rankings and personality. Start your message with a short greeting to {agent['name']} and then provide feedback."
            feedback = []
            for other_agent in agents:
                if other_agent != agent:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": f"You are {other_agent['name']}, {other_agent['persona']}. You are reviewing the rankings of another agent."},
                            {"role": "user", "content": feedback_prompt}
                        ],
                        max_tokens=600
                    )
                    feedback_content = response.choices[0].message.content.strip()
                    # Clean the response content
                    if feedback_content.startswith("```") and feedback_content.endswith("```"):
                        feedback_content = feedback_content[3:-3].strip()
                    feedback.append(f"{other_agent['name']}: {feedback_content}")

                    print(feedback_content)
                    print(f"This from agent {other_agent['name']}")
                    print("--------------------------------")

            
            step_feedback[agent["name"]] = feedback
            save_interaction(agent["name"], feedback, step, "feedback")
        
        # Each agent re-ranks items based on the feedback received
        for agent in agents:
            feedback_summary = " ".join(step_feedback[agent["name"]])
            rerank_prompt = f"Feedback received: {feedback_summary}. Now, reconsider and re-rank the items based on the feedback from your peers. Recall that this is the scenario of the game which you used to base your initial rankings {PROMPT}"
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are {agent['name']}, {agent['persona']}. Reconsider and re-rank the items. OUTPUT THE RANKINGS AS A DICTIONARY OF EACH ITEM WITH THE ITEM AND ITS CORRESPONDING RANKING. EACH RANKING MUST BE AN INTEGER BETWEEN 1 AND 15 INCLUSIVE AND EACH NUMBER MUST SHOW UP EXACTLY ONCE. DO NOT INCLUDE ANY MISCELLANEOUS INFORMATION. ONLY OUTPUT A DICTIONARY AND NAMES SHOULD BE EXACTLY AS BEFORE."},
                    {"role": "user", "content": rerank_prompt}
                ]
            )
            rerank_content = response.choices[0].message.content.strip()
            print(f"RERANK::: {rerank_content}")
            # Clean the response content
            if rerank_content.startswith("```") and rerank_content.endswith("```"):
                rerank_content = rerank_content[9:-3].strip()

            new_ranking = ast.literal_eval(rerank_content)
            rankings[agent["name"]] = new_ranking
            save_interaction(agent["name"], {"new_ranking": new_ranking}, step, "ranking")

    return rankings

