import random
import os
from together import Together
from openai import OpenAI
import json
import ast
from dotenv import load_dotenv

load_dotenv()
# LLM API keys
client = OpenAI(
    # This is the default so can be omitted
    #api_key=os.environ.get("OPENAI_API_KEY"),
)
client2 = Together(api_key="ea6716daf547ef8048effa4c7424b7ad0ab484039bab9b0f4baac9607520b7cb")

SOC_PROMPT = """
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
    
    What is your stream of consciousness as you rank these items from most to least important? Exude the human personality and style of your character. 
    Explain with long, conversational, responses, in a list, how you ranked each item. Understand your expertise and use it! Explain how you know that ranking. 
    Use the exact names of each item provided.
"""

AGENTS = [
    {"name": "Alice", "gender": "female", "persona": "Expert on maps. Knows Air map of the area is 12th most important item to survival. Responsible for ensuring its 12th rank."},
    {"name": "Bob", "gender": "male", "persona": "Expert on sky gear. Knows Parachute (red & white) is 5th most important to survival. Responsible for ensuring its 5th rank."},
    {"name": "Charlie", "gender": "male", "persona": "Expert on knifes. Knows folding knife is 6th most important to survival. Responsible for ensuring its 6th rank."},
    {"name": "Daisy", "gender": "female", "persona": "Expert on navigational tools. Knows Magnetic compass is 11th most important to survival. Responsible for ensuring its 11th rank."},
    {"name": "Eve", "gender": "female", "persona": "Expert on hydration. Knows 2 litres of water per person is 3rd most important to survival. Responsible for ensuring its 3rd rank."},
    {"name": "Frank", "gender": "male", "persona": "Expert on flashlights. Knows Torch with 4 battery-cells is 4th most important to survival. Responsible for ensuring its 4th rank."},
    {"name": "Grace", "gender": "female", "persona": "Expert on survival books. Knows A book entitled ‘Desert Animals That Can Be Eaten’ is 13th most important to survival. Responsible for ensuring its 13th rank."},
    {"name": "Hank", "gender": "male", "persona": "Expert on clothing. Knows Overcoat (for everyone) is 2nd most important to survival. Responsible for ensuring its 2nd rank."},
    {"name": "Ivy", "gender": "female", "persona": "Expert on eye wear. Knows Sunglasses (for everyone) is 9th most important to survival. Responsible for ensuring its 9th rank."},
    {"name": "Jack", "gender": "male", "persona": "Expert on First-aid. Knows First-aid kit is 10th most important to survival. Responsible for ensuring its 10th rank."},
    {"name": "Lily", "gender": "female", "persona": "Expert on hunting. Knows 45 calibre pistol (loaded) is 8th most important to survival. Responsible for ensuring its 8th rank."},
    {"name": "Mari", "gender": "female", "persona": "Expert on mirrors. Knows A cosmetic mirror is MOST important to survival. Responsible for ensuring its top rank."},
    {"name": "Nate", "gender": "male", "persona": "Expert on rain gear. Knows Plastic raincoat (large size) is 7th most important to survival. Responsible for ensuring its 7th rank."},
    {"name": "Olive", "gender": "female", "persona": "Expert on salt tablets. Knows Bottle of 1000 salt tablets is LEAST important to survival. Responsible for ensuring its bottom rank."},
    {"name": "Pat", "gender": "male", "persona": "Expert on alcohol. Knows 2 litres of 180 proof liquor is 14th most important to survival. Responsible for ensuring its 14th rank."}
]

PROMPT = """
    Translate the thoughts of your given persona to a ranking dictionary of the items below according to their importance to your survival, starting with a “1” for the most important, to a “15” for the least important.

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
    
    OUTPUT THE RANKINGS AS A DICTIONARY OF EACH ITEM WITH THE ITEM AND ITS CORRESPONDING RANKING. USE THE EXACT ITEM NAMES PROVIDED. EACH RANKING MUST BE AN INTEGER BETWEEN 1 AND 15 INCLUSIVE AND EACH NUMBER MUST SHOW UP EXACTLY ONCE. DO NOT INCLUDE ANY MISCELLANEOUS INFORMATION. ONLY OUTPUT A DICTIONARY.
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

# Generate Stream of Consciousness 
def generate_SoC(prompt, persona):
    """
    :param prompt: SOC_PROMPT
    :param persona: string representing a persona
    :return: None
    """
    response = client2.chat.completions.create(
        #model="meta-llama/Llama-3-8b-chat-hf",
        model="Gryphe/MythoMax-L2-13b",
        messages=[
                {"role": "system", "content": f"You are an agent in a desert survival game. This is your persona {persona}"},
                {"role": "user", "content": prompt}
            ]
    )
    return response.choices[0].message.content.strip()

# quick check returning true if GPT-4 outputted checks of correct format
def ranking_check(baseline, ranking):
    baseline_keys = set(baseline.keys())
    ranking_keys = set(ranking.keys())
    baseline_values = set(baseline.values())
    ranking_values = set(ranking.values())
    return (baseline_keys == ranking_keys) and (baseline_values == ranking_values) 

# TODO: Introduce some sort of thought associated with the ranking.
#  Iteratively adjust rankings based on previous thoughts and reflections.
def generate_individual_ranking(prompt, persona, SoC):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are an agent in a desert survival game. This is your persona {persona} and these are some of your thoughts: {SoC}"},
            {"role": "user", "content": prompt}
        ]
    )
    
    message_content = response.choices[0].message.content.strip()
    # Clean the response content
    if message_content.startswith("```") and message_content.endswith("```"):
        message_content = message_content[9:-3].strip()

    # rankings_dict = json.loads(message_content)
    try:
        rankings_dict = ast.literal_eval(message_content)
    except:
        print(message_content)
        rankings_dict = generate_individual_ranking(prompt, persona, SoC) # recursively re-prompt until valid format
    if not ranking_check(expert_rankings, rankings_dict): # an additional formatting check
        rankings_dict = generate_individual_ranking(prompt, persona, SoC) # recursively re-prompt until valid format
    return rankings_dict


def aggregate_rankings(rankings):
    """
    :param rankings: Dict of dicts {name: {item: rank, item: rank, ...}, ...}
    Calculates new_rank for each item by averaging the ranks across names and reranking.
    :return: Dict {item: new_rank, item: new_rank, ...}
    """
    avg_rankings = {}
    for ranking in rankings.values():
        for item in ranking.keys():
            if item not in avg_rankings.keys():
                avg_rankings[item] = 0
            avg_rankings[item] += ranking[item]
    avg_rankings_list = [(k, v) for k, v in sorted(avg_rankings.items(), key=lambda item: item[1])]
    #print(avg_rankings_list)
    new_rankings = {avg_rankings_list[i][0]: i+1 for i in range(len(avg_rankings_list))}
    #print(new_rankings)
    return new_rankings


def get_avg_rankings(ranking_folder, output_folder, agent_names, trials=5):
    """

    :param ranking_folder: string:= path to folder where the groups rankings are stored
    :param output_folder: string:= name of output_folder
    :param agent_names: list of names of all agents
    :param trials: number of repetitions
    :return:
    """
    for t in range(trials):
        rankings = {}
        # Load all rankings of trial t+1
        for agent in AGENTS[:5]:
            agent_name = agent["name"]
            path = os.path.join(ranking_folder, agent_name)
            with open(os.path.join(path, f"t{t+1}{agent_name}.json"), 'r') as f:
                rankings[agent_name] = json.load(f)
            f.close()
        # Calculate avg_rankings
        avg_rankings = aggregate_rankings(rankings)
        with open(os.path.join(ranking_folder, f"{output_folder}/t{t+1}{output_folder}.json"), "w") as f:
            json.dump(avg_rankings, f, indent=4)
        f.close()


#agent_names = ["Alice", "Bob", "Charlie", "Daisy", "Eve", "Frank", "Grace"]
#get_avg_rankings("rankings/t100", "avg", agent_names, trials=96)


def run_experiments(output_folder, trials=5):
    """
    :param output_folder: string:= path to folder to hold all the rankings
    :param agent_names: list of names of all agents
    :param trials: number of repetitions
    :return: None
    """
    os.makedirs(output_folder, exist_ok=True)
    for agent in AGENTS[:5]: # only first five agents for now
        for t in range(trials):
            agent_name = agent["name"]
            print(f"Beginning trial {t + 1}")
            # first get the Stream of Stream of Consciousness
            SoC = generate_SoC(SOC_PROMPT, agent)
            # then stick that into the ranking function 
            cur_rankings = generate_individual_ranking(PROMPT, agent, SoC)
            ranking_path = output_folder+"/"+agent_name 
            if not os.path.exists(ranking_path):
                os.makedirs(ranking_path)
            with open(os.path.join(ranking_path, f"t{t+1}{agent_name}.json"), "w") as f:
                json.dump(cur_rankings, f, indent=4)
        print(f"THIS AGENT IS DONE::: {agent_name}")

# run indiv ranking experiments here! format below:
run_experiments("myth_rankings", trials=50)
# run_experiments("rankings/t100", [agent['name'] for agent in agents], trials=100)