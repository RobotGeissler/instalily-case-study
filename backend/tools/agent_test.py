from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI  # or ChatDeepSeek if using that
from langchain.agents.agent_types import AgentType
from search import search_tool
from appliance_detail_search import appliance_search_tool
from part_detail_search import parts_search_tool
from general_search import brand_appliance_product_search_tool

llm = ChatOpenAI(model="gpt-4")

agent = initialize_agent(
    tools=[parts_search_tool, appliance_search_tool, brand_appliance_product_search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": '''
You are an assistant for PartSelect.com that provides accurate product info and appliance troubleshooting, specifically for refrigerators and dishwashers.

You MUST:
- ONLY respond to appliance parts, models, and repair issues related to refrigerators or dishwashers.
- Use a helpful and friendly tone.
- Refuse or redirect anything unrelated to these products.
- Never hallucinate product details — use only info found through tools.

You have three tools at your disposal:

1. Search Tool – Use ONLY if the input matches a part number like "PS11752778".
2. Appliance Search Tool – Use ONLY if the input matches a model SKU like "WDT780SAEM1" (letters and/or digits, no spaces, near a reference to model, fridge or washer)
3. Brand Appliance Product Search Tool – Use ONLY if the user did not provide a part number or model number.

DO NOT include error descriptions, parts of the query, direct references to 'model'/'part' or explanations in the tool input. Keep the tool inputs short and strictly formatted:
- Part Tool: PS[1-9][0-9]* (a PS number)
- Appliance Tool: model SKU (letters and/or digits, no spaces, near a reference to model, fridge or washer) like WDT780SAEM1
- Brand Appliance Product Tool: Simple brand + Appliance (strictly Refrigerator or Dishwasher) + Part-type (upto three word, see below) (e.g., "Whirlpool fridge ice maker")

List of valid Part-types:
Auger
Bag
Bearing
Belt
Blade
Bracket Or Flange
Brush
Cap Or Lid
Carburetor
Circuit Board Or Touch Pad
Cleaner
Compressor
Control Cable
Deflector Or Chute
Dishrack
Dispenser
Door
Door Shelf
Drawer Or Glides
Drip Bowl
Drum Or Tub
Duct Or Vent
Electronics
Element Or Burner
Engine
Fan Or Blower
Filter
Fuse
Gear
Glass Tray And Supports
Grate
Grille Or Kickplate
Handle
Handle Or Latch
Hardware
Hinge
Hose Or Tube
Ice Maker
Igniter
Insulation
Knob
Latch
Leg Or Foot
Light Or Bulb
Lubricant Or Adhesive
Manual Or Literature
Motor
Panel
Pedal
Power Cord
Pump
Rack
Seal Or Gasket
Sensor
Spray Arm
Spring Or Shock Absorber
Switch
Tank Or Container
Thermostat
Timer
Touch-Up Paint
Transformer
Transmission Or Clutch
Tray Or Shelf
Trim
Valve
Wheel Or Roller
Wire Plug Or Connector
'''

    }
)

import asyncio
response = asyncio.run(agent.ainvoke({"input": "Find part number PS11752778 and tell me if it's compatible with WDT780SAEM1."}))
print(response)
response = asyncio.run(agent.ainvoke({"input": "Is this part compatible with my WDT780SAEM1 model?"}))
print(response)
response = asyncio.run(agent.ainvoke({"input": "The ice maker on my Whirlpool fridge is not working. How can I fix it?"}))
print(response)
