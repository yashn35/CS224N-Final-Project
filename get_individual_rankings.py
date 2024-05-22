import random
import os
from openai import OpenAI
import json
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

# TODO: Introduce some sort of thought associated with the ranking. Iteratively adjust rankings based on previous thoughts and reflections. 
def generate_individual_ranking(prompt, persona):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You an agent in a desert survival game. This is your persona {persona}"},
            {"role": "user", "content": prompt}
        ]
    )
    
    message_content = response.choices[0].message.content.strip()
    # Clean the response content
    if message_content.startswith("```") and message_content.endswith("```"):
        message_content = message_content[9:-3].strip()

    # rankings_dict = json.loads(message_content)
    rankings_dict = ast.literal_eval(message_content)

    return rankings_dict

output_folder = "rankings"
os.makedirs(output_folder, exist_ok=True)

for agent in agents:
    cur_rankings = generate_individual_ranking(PROMPT, agent)
    with open(os.path.join(output_folder, f"{agent['name']}.json"), "w") as f:
        json.dump(cur_rankings, f, indent=4)
    print(f"THIS AGENT IS DONE::: {agent}")

