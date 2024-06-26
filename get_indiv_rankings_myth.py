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
client2 = Together(api_key="YOUR TOGETHER API KEY")

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
    
    What is your stream of consciousness, based on your persona, as you rank these items from most to least important to your survival? 
    Higher ranks (low numbered) at the start of the list are what you believe to be most important. Lower ranks (high numbered) at the end of the list are what you believe to be least important.
    Exude the human personality and style of your persona. Explain each ranking with long, conversational responses and do so in list format.
    Write in first person. Use the given names for each of the 15 items. Stick to these 15 items!
"""

AGENTS = [
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

# function to generate a stream of consciousness reaction to the prompt for a persona
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
                {"role": "system", "content": f"You are an agent in a desert survival game. This is your persona which you must strictly roleplay as {persona}"},
                {"role": "user", "content": prompt}
            ]
    )
    return response.choices[0].message.content.strip()


# quick check returning true if GPT-4o outputted correct format
def ranking_check(baseline, ranking):
    baseline_keys = set(baseline.keys())
    ranking_keys = set(ranking.keys())
    baseline_values = set(baseline.values())
    ranking_values = set(ranking.values())
    return (baseline_keys == ranking_keys) and (baseline_values == ranking_values) 


# function returning individual ranking based on a persona and its stream of consciousness reaction to the prompt
def generate_individual_ranking(prompt, persona, SoC):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are an agent in a desert survival game. These are some of your thoughts: {SoC}"},
            {"role": "user", "content": prompt}
        ]
    )
    
    message_content = response.choices[0].message.content.strip()
    # Clean the response content
    if message_content.startswith("```") and message_content.endswith("```"):
        message_content = message_content[9:-3].strip()

    try:
        rankings_dict = ast.literal_eval(message_content)
    except:
        print(message_content)
        rankings_dict = generate_individual_ranking(prompt, persona, SoC) # recursively re-prompt until valid format
    if not ranking_check(expert_rankings, rankings_dict): # an additional formatting check
        rankings_dict = generate_individual_ranking(prompt, persona, SoC) # recursively re-prompt until valid format
    return rankings_dict


# function to call to run experiments for a certain number of trials. Results are dumped into output_folder.
def run_experiments(output_folder, trials=5):
    """
    :param output_folder: string:= path to folder to hold all the rankings
    :param agent_names: list of names of all agents
    :param trials: number of repetitions
    :return: None
    """
    os.makedirs(output_folder, exist_ok=True)
    for agent in AGENTS: # AGENTS[:5] if seeking only first five agents
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
run_experiments("myth_rankings_t5", trials=5)
