import os 
import json

import numpy as np
import pandas as pd
# TODO: Generate a function that gives them a score

agents = [
    {"name": "Alice", "gender": "female", "persona": "Expert on maps. Knows Air map of the area is 12th most important item on the list."},
    {"name": "Bob", "gender": "male", "persona": "Expert on sky gear. Knows Parachute (red & white) is 5th most important item on the list."},
    {"name": "Charlie", "gender": "male", "persona": "Expert on knifes. Knows folding knife is 6th most important item on the list."},
    {"name": "Daisy", "gender": "female", "persona": "Expert on navigational tools. Knows Magnetic compass is 11th most important item on the list."},
    {"name": "Eve", "gender": "female", "persona": "Expert on hydration. Knows 2 litres of water per person is 3rd most important item on the list."},
    {"name": "Frank", "gender": "male", "persona": "Expert on flashlights. Knows Torch with 4 battery-cells is 4th most important item on the list."},
    {"name": "Grace", "gender": "female", "persona": "Expert on survival books. Knows A book entitled ‘Desert Animals That Can Be Eaten’ is 13th most important item on the list."},
    {"name": "Hank", "gender": "male", "persona": "Expert on clothing. Knows Overcoat (for everyone) is 2nd most important item on the list."},
    {"name": "Ivy", "gender": "female", "persona": "Expert on eye wear. Knows Sunglasses (for everyone) is 9th most important item on the list."},
    {"name": "Jack", "gender": "male", "persona": "Expert on First-aid. Knows First-aid kit is 10th most important item on the list."},
    {"name": "Lily", "gender": "female", "persona": "Expert on hunting. Knows 45 calibre pistol (loaded) is 8th most important item on the list."},
    {"name": "Mari", "gender": "female", "persona": "Expert on mirrors. Knows A cosmetic mirror is MOST important item on the list."},
    {"name": "Nate", "gender": "male", "persona": "Expert on rain gear. Knows Plastic raincoat (large size) is 7th most important item on the list."},
    {"name": "Olive", "gender": "female", "persona": "Expert on salt tablets. Knows Bottle of 1000 salt tablets is LEAST important item on the list."},
    {"name": "Pat", "gender": "male", "persona": "Expert on alcohol. Knows 2 litres of 180 proof liquor is 14th most important item on the list."}
]
expert_rankings = {
    "Torch with 4 battery-cells": 4,
    "Folding knife": 6,
    "Air map of the area": 12,
    "Plastic raincoat (large size)": 7,
    "Magnetic compass": 11,
    "First-aid kit": 10,
    "45 calibre pistol (loaded)": 8,
    "Parachute (red & white)": 5,
    "Bottle of 1000 salt tablets": 15,
    "2 litres of water per person": 3,
    "A book entitled ‘Desert Animals That Can Be Eaten’": 13,
    "Sunglasses (for everyone)": 9,
    "2 litres of 180 proof liquor": 14,
    "Overcoat (for everyone)": 2,
    "A cosmetic mirror": 1
}

# Function to calculate the score for each participant
# According to this paper: An Input-Process-Output Analysis of Influence and Performance in Problem-Solving Groups
def calculate_score(baseline, ranking):
    score = 0
    for item, correct_rank in baseline.items():
        participant_rank = ranking.get(item)
        if participant_rank is not None:
            score += abs(correct_rank - participant_rank)
    return 122-score


def calculate_influence(group, ranking):
    infl = 0
    for item, group_rank in group.items():
        participant_rank = ranking.get(item)
        if participant_rank is not None:
            infl += abs(group_rank - participant_rank)
    return -infl


#print(calculate_score(expert_rankings, p1_items))
#print(calculate_score(expert_rankings, p2_items))
#print(calculate_score(expert_rankings, p3_items))
#print(calculate_score(expert_rankings, p4_items))
#print(calculate_score(expert_rankings, p12_items))


#print(calculate_influence(p12_items, p1_items))
#print(calculate_influence(p12_items, p2_items))
#print(calculate_influence(p12_items, p3_items))


def get_group_scores(path, trials=5):
    """
    :param path: Path to group scores
           trials: Number of times each experiment was run
    :return: array of shape: (trials,) containing the group score for each trial,
             dict: {agent_name: [influence of trial i, ...]} mapping agents to list of influence for each trial
    """
    group_rankings = []
    group_scores = []
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), "r") as f:
            group = json.load(f)
        f.close()
        group_rankings.append(group)
        score = calculate_score(expert_rankings, group)
        group_scores.append(score)
    print(group_scores)
    infls = {}
    for t in range(trials):
        print(f'Trial {t+1}')
        for agent in agents:
            if agent['name'] not in infls.keys():
                infls[agent['name']] = []
            path = os.path.join(f"rankings/{agent['name']}", f"t{t+1}{agent['name']}.json")
            with open(path, "r") as f:
                ranking = json.load(f)
            f.close()
            group = group_rankings[t]
            infls[agent['name']].append(calculate_influence(group, ranking))
    print(infls)
    return group_scores, infls


#group_scores, infls = get_group_scores("rankings/avg")
#df = pd.DataFrame.from_dict(infls)
#df.to_csv("indiv_infls_100.csv")
#print(df.mean(axis=0))

# quick check returning true if GPT-4 outputted checks of correct format
def ranking_check(baseline, ranking):
    baseline_keys = set(baseline.keys())
    ranking_keys = set(ranking.keys())
    return baseline_keys == ranking_keys

def get_indiv_scores(ranking_path, expert_rankings):
    scores = {}
    for agent in agents[:5]: # first five for now
        agent_name = agent["name"]
        scores[agent_name] = []
        print(f"Getting {agent_name} scores")
        path = os.path.join(ranking_path, agent_name)
        for filename in os.listdir(path):
            if "97" in filename or "98" in filename or "99" in filename or "100" in filename:
                pass
            else:
                with open(os.path.join(path, filename), "r") as f:
                    ranking = json.load(f)
                if ranking_check(expert_rankings, ranking): # make sure ranking is of correct form!
                    score = calculate_score(expert_rankings, ranking)
                    scores[agent_name].append(score)
        scores[agent_name] = scores[agent_name][:23] # keep only a portion by which we know are good, non-deformed data
    return scores

### Conduct indiv trials here with this template
ranking_path = "CS224N-Final-Project-main/myth_rankings_t80"
df = pd.DataFrame.from_dict(get_indiv_scores(ranking_path, expert_rankings))
df.to_csv("myth_indiv_scores_80.csv")
print(df.mean(axis=0))

#agent_names = ["Alice", "Bob", "Charlie", "Daisy", "Eve", "Frank", "Grace"]
#ranking_path = "rankings/t100"
#df = pd.DataFrame.from_dict(get_indiv_scores(ranking_path, expert_rankings, agent_names))
#df.to_csv("indiv_scores_96.csv")
#print(df.mean(axis=0))


#df = pd.read_csv("indiv_scores_5.csv")
#print(df.mean(axis=0))


# Load each JSON file and calculate the score
# TODO: update to work with trials
def get_feedback_scores(expert_rankings):
    # Folder containing the individual ranking JSON files
    input_folder = "interactions"
    # Create a list to store the scores
    scores = []
    for filename in os.listdir(input_folder):
        if filename.endswith("ranking_0.json"):
            with open(os.path.join(input_folder, filename), "r") as f:
                ranking = json.load(f)
                ranking = ranking['new_ranking']
                print(ranking)
            participant_name = filename.split("_")[0]
            print(participant_name)
            score = calculate_score(expert_rankings, ranking)

            scores.append({"Participant": participant_name, "Score": score})

    # Convert scores to DataFrame
    scores_df = pd.DataFrame(scores)

    # Save scores to CSV
    scores_df.to_csv("after_feedback_scores.csv", index=False)

    print("Scores saved to scores.csv")