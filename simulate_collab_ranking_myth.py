import os
import random
import json
import numpy as np
from together import Together
from openai import OpenAI
import ast

# Set up all API keys
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    # This is the default so can be omitted
    # api_key=""
)
client2 = Together(api_key="YOUR TOGETHER API KEY")

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

REC_PROMPT = """
    It is around 10:00 am in July and you have just crash landed in an unknown position within the Atacama Desert in South America. The pilot, co-pilot, and twin-engined plane have been irreversibly burnt to skeletons. Thankfully, none of you were injured.

    Before impact, the pilot indicated you're 50 miles from a mining camp, the nearest settlement, and 65 miles off course. The immediate area is quite flat, except for occasional cacti, and seems rather barren. The last weather report indicated that the temperature would reach 110 F today, corresponding to ground level temperature 130 F.

    You're in lightweight clothes: short-sleeved shirts, pants, socks, and street shoes. Everyone has a handkerchief and collectively, you have 3 packs of cigarettes and a ballpoint pen.

    Before your plane caught fire, your group was able to salvage the 15 items listed below. Your task is to rank these items according to their importance to your survival, starting with a “1” for the most important, to a “15” for the least important.

    Torch with 4 battery-cells [#]
    Folding knife [#]
    Air map of the area [#]
    Plastic raincoat (large size) [#]
    Magnetic compass [#]
    First-aid kit [#]
    45 calibre pistol (loaded) [#]
    Parachute (red & white) [#]
    Bottle of 1000 salt tablets [#]
    2 litres of water per person [#]
    A book entitled ‘Desert Animals That Can Be Eaten’ [#]
    Sunglasses (for everyone) [#]
    2 litres of 180 proof liquor [#]
    Overcoat (for everyone) [#]
    A cosmetic mirror [#]
"""

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
    {"name": "Jack", "gender": "male", "persona": "Doctor who firmly knows the First-aid kit is irrelevant. Given that everyone is currently healthy, he wants rank the First Aid kit as 10th."},
    {"name": "Lily", "gender": "female", "persona": "She is a very balanced person. While she knows the pistol can defend and signal, she knows it is otherwise useless and ranks it as 8th."},
    {"name": "Mari", "gender": "female", "persona": "Expert survivalist who knows for a fact that the cosmetic mirror is most important for survival in this scenario (best and most efficient way to reflect a signal and get rescued). Must rank it 1. and convince others to do the same."},
    {"name": "Nate", "gender": "male", "persona": "He does not care about the large Plastic raincoat and ranks it in limbo since it can collect dew."},
    {"name": "Olive", "gender": "female", "persona": "Expert survivalist who knows the Bottle of 1000 salt tablets has no use in the desert and is the worst item for survival in this scenario. Must rank it 15. and convince others to do the same."},
    {"name": "Pat", "gender": "male", "persona": "Bartender who knows that Liquor can be used as an antiseptic. But otherwise knows liquor is one of the worst and most useless items."}
]

agent_names = [a['name'] for a in agents]
"""
agent_names = [ "Alice", "Bob", "Charlie", "Daisy", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack", "Lily", 
               "Mari", "Nate", "Olive", "Pat"]
"""

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

# keep these folders in mind for later
output_folder = "myth_rankings_t5"
interaction_folder = "myth_interactions"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(interaction_folder, exist_ok=True)

# function loading rankings from get_indiv_rankings_myth.py
def load_rankings(agent_names, path, t):
    rankings = {}
    for agent in agent_names:
        filename = os.path.join(path, f"{agent}/t{t}{agent}.json")
        with open(filename, "r") as f:
            rankings[agent] = json.load(f)
    return rankings


# function to check if the agents agree on a ranking 
def check_converge(items_explanations, key):
    """
    :param rankings_explanations: dict of dicts. {agent_name: {key, 'explanation'}}
    :return: True if all agents in rankings_explanations have the same preferred ranking. False otherwise
    """
    chosen_names = [agent[key] for agent in items_explanations.values()]
    return chosen_names[1:] == chosen_names[:-1]


# save interaction for one trial, interaction, step, type, and agent
def save_interaction(agent_name, interaction, step, type, t):
    with open(os.path.join(interaction_folder, f"{agent_name}_{type}_{step}_t{t}.json"), "w") as f:
        json.dump(interaction, f, indent=4)


# quick check returning true if GPT-4 outputted correct format
def ranking_check(baseline, ranking):
    baseline_keys = set(baseline.keys())
    ranking_keys = set(ranking.keys())
    baseline_values = set(baseline.values())
    ranking_values = set(ranking.values())
    return (baseline_keys == ranking_keys) and (baseline_values == ranking_values) 


# returns new ranking dictionary given agent and all the feedback given to that agent 
def return_new_ranking(agent, feedback_summary):
    reaction_prompt = f"""
             Feedback received from peers: {feedback_summary}. 
  
            Use the feedback to inform your new ranking. Strictly and logically role playing as your persona in 
            this scenario receiving feedback from your peers, explain with long, conversational, responses, in a list, how you now want to 
            rank each item. Note that higher ranks (low numbered) at the start of the list are most important while lower ranks
            (high numbered) at the end of the list are least important. Include all 15 items.
            """
    response = client2.chat.completions.create(
            model="Gryphe/MythoMax-L2-13b",
            messages=[
                {"role": "system", "content": f"Your agent persona is {agent}. Previously, you ranked items in the game {REC_PROMPT}"},
                {"role": "user", "content": reaction_prompt}
        ]
    )
    feedback_reaction = response.choices[0].message.content.strip()
    rerank_prompt = f"Internal thoughts: {feedback_reaction} Translate the internal thoughts of your persona into the desired output dictionary in {PROMPT}:"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
             {"role": "system", "content": f"""Your agent persona is {agent}. Reconsider and re-rank the items. OUTPUT THE RANKINGS AS A DICTIONARY OF EACH ITEM WITH THE ITEM AND ITS CORRESPONDING RANKING. EACH RANKING MUST BE AN INTEGER BETWEEN 1 AND 15 INCLUSIVE AND EACH NUMBER MUST SHOW UP EXACTLY ONCE. DO NOT INCLUDE ANY MISCELLANEOUS INFORMATION. ONLY OUTPUT A DICTIONARY AND NAMES SHOULD BE EXACTLY AS BEFORE (SAME EXACT CHARS)."""},
            {"role": "user", "content": rerank_prompt}
        ]
    )
    rerank_content = response.choices[0].message.content.strip()
    agent_name = agent["name"]
    print(f"RERANK {agent_name}::: {rerank_content}")
    # Clean the response content
    if rerank_content.startswith("```") and rerank_content.endswith("```"):
        rerank_content = rerank_content[9:-3].strip()
    try:
        return ast.literal_eval(rerank_content)
    except:
        return return_new_ranking(agent, feedback_summary)


# One round of feedback for one trial (like with direct prompting, each agent gets 10 reviewers)
def simulate_discussion(rankings, t):
    for step in range(1):  # Rounds of discussion, that is feedback back and forth
        step_feedback = {}
        
        # Collect feedback from all agents for each agent
        for agent in agents:     # all 15 agents 
            print(f"Current agent: {agent}")
            agent_name = agent["name"]
            feedback_prompt = f"""
            Recall that 1 is highest rank, which goes down to 15, lowest rank. 
            Your peer agent {agent['name']} has the following individual ranking: {rankings[agent['name']]}. 
            You currently think the correct ranking is {rankings[agent_name]}
            Provide your feedback on {agent['name']}'s rankings while exuding the human personality and style of your character.
            Greet {agent['name']} and then concisely provide what you believe to be the most important feedback, logically and 
            strictly being your given persona. Be your character and be concise, convincing, and logical.
            """
            feedback = []
            feedback_agents = random.sample(agents, 10) # keep amount of feedback same as first experiment: 10
            for other_agent in feedback_agents: 
                if other_agent != agent:
                    response = client2.chat.completions.create(
                        model="Gryphe/MythoMax-L2-13b",
                        messages=[
                            {"role": "system", "content": f"Your agent persona is {other_agent}. Recall that previously you ranked items in the game {REC_PROMPT} You are reviewing the rankings of another agent."},
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
            save_interaction(agent["name"], feedback, step, "feedback", t)
        
        # Each agent re-ranks items based on the feedback received
        for agent in agents:
            agent_name = agent["name"]
            feedback_summary = " ".join(step_feedback[agent_name])
            new_ranking = return_new_ranking(agent, feedback_summary)
            
            # special char switch-up by GPT-4o
            if "A book entitled 'Desert Animals That Can Be Eaten'" in new_ranking:
                new_ranking["A book entitled ‘Desert Animals That Can Be Eaten’"] = new_ranking["A book entitled 'Desert Animals That Can Be Eaten'"]
                new_ranking.pop("A book entitled 'Desert Animals That Can Be Eaten'", None)
            while not ranking_check(expert_rankings, new_ranking):
                new_ranking = return_new_ranking(agent, feedback_summary)
                # special char switch-up by GPT-4o
                if "A book entitled 'Desert Animals That Can Be Eaten'" in new_ranking:
                    new_ranking["A book entitled ‘Desert Animals That Can Be Eaten’"] = new_ranking["A book entitled 'Desert Animals That Can Be Eaten'"]
                    new_ranking.pop("A book entitled 'Desert Animals That Can Be Eaten'", None)
                    
            rankings[agent_name] = new_ranking
            save_interaction(agent_name, {"new_ranking": new_ranking}, step, "ranking", t)

    return rankings


# function and code to run five trials (or custom if needed) of the feedback discussion 
rankings = {}
def run_discussion_trials(agent_names, path, trials=5):
    for t in range(trials):
        rankings = load_rankings(agent_names, path, t + 1) 
        simulate_discussion(rankings, t + 1)
run_discussion_trials(agent_names, output_folder)