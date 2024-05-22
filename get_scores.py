import os 
import json
import pandas as pd
# TODO: Generate a function that gives them a score 
# Folder containing the individual ranking JSON files
input_folder = "interactions"

baseline_rankings = {
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
def calculate_score(baseline, ranking):
    score = 0
    for item, correct_rank in baseline.items():
        participant_rank = ranking.get(item)
        if participant_rank is not None:
            score += abs(correct_rank - participant_rank)
    return score

# Create a list to store the scores
scores = []

# Load each JSON file and calculate the score
for filename in os.listdir(input_folder):
    if filename.endswith("ranking_0.json"):
        with open(os.path.join(input_folder, filename), "r") as f:
            ranking = json.load(f)
            ranking = ranking['new_ranking']
            print(ranking)
        participant_name = filename.split("_")[0]
        print(participant_name)
        score = calculate_score(baseline_rankings, ranking)
        
        scores.append({"Participant": participant_name, "Score": score})

# Convert scores to DataFrame
scores_df = pd.DataFrame(scores)

# Save scores to CSV
scores_df.to_csv("after_feedback_scores.csv", index=False)

print("Scores saved to scores.csv")