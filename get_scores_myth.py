import os 
import json

import numpy as np
import pandas as pd

agents = [
    {"name": "Alice", "gender": "female", "persona": "Knows that Air maps help with getting an idea on the location but are otherwise pretty useless and not important for survival."},
    {"name": "Bob", "gender": "male", "persona": "Knows that The parachute is the 5th best out of 15 items because it can be used for signaling and creating shelter, making it quite versatile. Yet, water and light (torch) are more critical, amongst others."},
    {"name": "Charlie", "gender": "male", "persona": "He strongly agrees that knifes are not useful beyond cutting. Will rank it 6th."},
    {"name": "Daisy", "gender": "female", "persona": "Rescue expert who knows that the nearest help is way too far away for the magnetic compass to be useful. She still wants to rank it 11th just in case."},
    {"name": "Eve", "gender": "female", "persona": "An expert on hydration. Expertise confirms that 2 liters of water per person is the 3rd most important survival item."},
    {"name": "Frank", "gender": "male", "persona": "He does not think the torch with 4 battery-cells is important and thinks it's meh. But others may need a night light."},
    {"name": "Grace", "gender": "female", "persona": "Used A book entitled ‘Desert Animals That Can Be Eaten’ before. Eating wastes precious body water so she vows to not use the book and waste water."},
    {"name": "Hank", "gender": "male", "persona": "Great fan of Overcoat who knows that it's essential protection in the desert. The overcoat is a matter of life and death, second only to the hope of rescue."},
    {"name": "Ivy", "gender": "female", "persona": "Read that sunglasses protect against glare. She concludes that sunglasses are important to survival and will rank it amongst the top ten."},
    {"name": "Jack", "gender": "male", "persona": "Doctor who firmly knows the First-aid kit is irrelevant. Given that everyone is currently healthy, he wants to rank the First Aid kit as 10th."},
    {"name": "Lily", "gender": "female", "persona": "She is a very balanced person. While she knows the pistol can defend and signal, she knows it is otherwise useless and ranks it as 8th."},
    {"name": "Mari", "gender": "female", "persona": "Expert survivalist who knows for a fact that the cosmetic mirror is most important for survival in this scenario (best and most efficient way to reflect a signal and get rescued). Must rank it 1. and convince others to do the same."},
    {"name": "Nate", "gender": "male", "persona": "He does not care about the large Plastic raincoat and ranks it in limbo since it can collect dew."},
    {"name": "Olive", "gender": "female", "persona": "Expert survivalist who knows the Bottle of 1000 salt tablets has no use in the desert and is the worst item for survival in this scenario. Must rank it 15. and convince others to do the same."},
    {"name": "Pat", "gender": "male", "persona": "Bartender who knows that Liquor can be used as an antiseptic. But otherwise knows liquor is one of the worst and most useless items."}
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

# function to calculate the score for each participant
# According to this paper: An Input-Process-Output Analysis of Influence and Performance in Problem-Solving Groups
def calculate_score(baseline, ranking):
    score = 0
    for item, correct_rank in baseline.items():
        participant_rank = ranking.get(item)
        if participant_rank is not None:
            score += abs(correct_rank - participant_rank)
    return 122-score


# function to calculate influence for each participant
# According to this paper: An Input-Process-Output Analysis of Influence and Performance in Problem-Solving Groups
def calculate_influence(group, ranking):
    infl = 0
    for item, group_rank in group.items():
        participant_rank = ranking.get(item)
        if participant_rank is not None:
            infl += abs(group_rank - participant_rank)
    return -infl


# function returning the indiv scores as a dict mapping agent name to list of scores 
# finds indiv rankings in path ranking_path and compares with expert_rankings 
def get_indiv_scores(ranking_path, expert_rankings):
    scores = {}
    for agent in agents: # agents[:5] for first five only
        agent_name = agent["name"]
        scores[agent_name] = []
        print(f"Getting {agent_name} scores")
        path = os.path.join(ranking_path, agent_name)
        for filename in os.listdir(path):
            with open(os.path.join(path, filename), "r") as f:
                    ranking = json.load(f)
            score = calculate_score(expert_rankings, ranking)
            scores[agent_name].append(score)
    return scores


"""
Conduct indiv trials here with this template
ranking_path = "myth_rankings_t5"
df = pd.DataFrame.from_dict(get_indiv_scores(ranking_path, expert_rankings))
df.to_csv("myth_indiv_scores_5.csv")
print(df.mean(axis=0))
"""

# function that loads each JSON file in the interaction folder containing each agent's post
# feedback rankings and calculate the post feedback scores. Can be done for desired no of trials
def get_feedback_scores(expert_rankings, trials=5):
    # Folder containing the individual ranking JSON files
    input_folder = "myth_interactions"
    # Create a list to store the scores
    scores = {}
    for agent_name in [a["name"] for a in agents]:
        scores[agent_name] = []
    for t in range(trials):
        for filename in os.listdir(input_folder):
            if filename.endswith(f"ranking_0_t{t + 1}.json"):
                with open(os.path.join(input_folder, filename), "r") as f:
                    ranking = json.load(f)
                    ranking = ranking['new_ranking']
                    print(ranking)
                participant_name = filename.split("_")[0]
                print(participant_name)
                scores[participant_name].append(calculate_score(expert_rankings, ranking)) 

    # Convert scores to DataFrame
    scores_df = pd.DataFrame.from_dict(scores)

    # Save scores to CSV
    scores_df.to_csv("after_feedback_scores_myth.csv", index=False)

    print("Scores saved to scores.csv")
    print(scores_df.mean(axis=0))

# get feedback scores with this template 
# get_feedback_scores(expert_rankings, trials=5)
