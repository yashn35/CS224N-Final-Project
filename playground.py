import os
import json
import numpy as np
from openai import OpenAI
import ast

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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
A book entitled ‘Desert Animals That Can Be Eaten’ [RANKING]
Sunglasses (for everyone) [RANKING]
2 litres of 180 proof liquor [RANKING]
Overcoat (for everyone) [RANKING]
A cosmetic mirror [RANKING]

OUTPUT THE RANKINGS AS A DICTIONARY OF EACH ITEM WITH THE ITEM AND ITS CORRESPONDING RANKING. EACH RANKING MUST BE AN INTEGER BETWEEN 1 AND 15 INCLUSIVE AND EACH NUMBER MUST SHOW UP EXACTLY ONCE. DO NOT INCLUDE ANY MISCELLANEOUS INFORMATION. ONLY OUTPUT A DICTIONARY.
"""

agents = [
    {"name": "Grace", "gender": "female", "persona": "a calm and collected decision-maker"},
    {"name": "Hank", "gender": "male", "persona": "a strategic and analytical thinker"},
    {"name": "Ivy", "gender": "female", "persona": "an empathetic and cooperative team player"},
    {"name": "Jack", "gender": "male", "persona": "a curious and open-minded explorer"}
]

# test = ['Grace_feedback_0.json', 'Hank_feedback_0.json', 'Ivy_feedback_0.json', 'Jack_feedback_0.json']

# Assuming the files are in the same directory
test_files = ['interactions/Grace_feedback_0.json', 'interactions/Hank_feedback_0.json', 'interactions/Ivy_feedback_0.json', 'interactions/Jack_feedback_0.json']

# Load feedback from files
feedback_data = {}
for file in test_files:
    with open(file, 'r') as f:
        agent_name = file.split('_')[0]
        print(agent_name)
        feedback_data[agent_name] = json.load(f)



def save_interaction(agent_name, interaction, step, type):
    with open(os.path.join("interactions", f"{agent_name}_{type}_{step}.json"), "w") as f:
        json.dump(interaction, f, indent=4)


for agent in agents:
            path = f"interactions/{agent['name']}"
            feedback_summary = " ".join(feedback_data[path])
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
            # rankings[agent["name"]] = new_ranking
            save_interaction(agent["name"], {"new_ranking": new_ranking}, 0, "ranking")