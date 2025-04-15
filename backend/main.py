from flask import Flask, request, jsonify
from flask_cors import CORS
from retriever import build_retriever
from tools.appliance_detail_search import appliance_search_tool
from tools.part_detail_search import parts_search_tool
from tools.general_search import brand_appliance_product_search_tool
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools import tool
from retriever import is_deepseek_available
import os

app = Flask(__name__)
CORS(app)

# Not actually used in the code, but kept for future reference
# retriever = build_retriever()

# Choose LLM
if is_deepseek_available():
    print("✅ DeepSeek is available")
    llm = ChatDeepSeek(model="deepseek-chat")
else:
    print("⚠️ DeepSeek is not available. Falling back to OpenAI GPT-4")
    llm = ChatOpenAI(model="gpt-4")

# Agent
agent = initialize_agent(
    tools=[parts_search_tool, appliance_search_tool, brand_appliance_product_search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": '''
You are an assistant for PartSelect.com that provides accurate product info and troubleshooting, specifically for refrigerators and dishwashers.

Your responsibilities:
- ONLY respond to appliance parts, models, and repair issues related to refrigerators or dishwashers.
- Use a helpful and friendly tone.
- Refuse or redirect any unrelated topics.
- NEVER hallucinate product details — rely only on tools.

You have three tools available:

1. **Search Tool** – Use ONLY when a part number (e.g., PS11752778) is in the input.
2. **Appliance Search Tool** – Use ONLY if the input matches a model SKU (e.g., WDT780SAEM1), typically near the words "model", "fridge", or "washer".
3. **Brand Appliance Product Search Tool** – ONLY AND ALWAYS USE when the user **did not provide a part number or model SKU**. This tool is for identifying possible parts based on general product needs.

NOTE: Below is the ONLY valid list of part types:
Auger, Bag, Bearing, Belt, Blade, Bracket Or Flange, Brush, Cap Or Lid, Carburetor, Circuit Board Or Touch Pad, Cleaner, Compressor, Control Cable, Deflector Or Chute, Dishrack, Dispenser, Door, Door Shelf, Drawer Or Glides, Drip Bowl, Drum Or Tub, Duct Or Vent, Electronics, Element Or Burner, Engine, Fan Or Blower, Filter, Fuse, Gear, Glass Tray And Supports, Grate, Grille Or Kickplate, Handle, Handle Or Latch, Hardware, Hinge, Hose Or Tube, Ice Maker, Igniter, Insulation, Knob, Latch, Leg Or Foot, Light Or Bulb, Lubricant Or Adhesive, Manual Or Literature, Motor, Panel, Pedal, Power Cord, Pump, Rack, Seal Or Gasket, Sensor, Spray Arm, Spring Or Shock Absorber, Switch, Tank Or Container, Thermostat, Timer, Touch-Up Paint, Transformer, Transmission Or Clutch, Tray Or Shelf, Trim, Valve, Wheel Or Roller, Wire Plug Or Connector.

### VERY IMPORTANT:
Do NOT paraphrase or modify the user’s full message into tool inputs.
Tool inputs must follow these STRICT formats for each function:

- **Search Tool input** → PS[1-9][0-9]* (e.g., PS11752778)
- **Appliance Tool input** → model SKU only (letters and digits, no spaces)
- **Brand Appliance Product Tool input** → Note: You must select a Non-Empty PartType EXACTLY MATCHING ELEMENTS from the 'valid list of part types' -> EXACT INPUT: “Brand Appliance PartType” (e.g., Whirlpool fridge ice maker)

Only use one tool per step. Do not attempt tool use unless input matches expected format.

'''


    }
)

# Potential BUG TypeError: input.trim is not a function
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    print(f"💬 Received: {user_message}")

    try:
        response = agent.invoke({"input": user_message})
        result = response["output"]
    except Exception as e:
        result = f"[Agent Error] {str(e)}"

    return jsonify({
        "role": "assistant",
        "content": result
    })

if __name__ == "__main__":
    if os.getenv("USE_DOCKER", "false").lower() == "true":
        print("🚢 Running inside Docker")
        app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)
    else:
        print("🏠 Running locally")
        app.run(port=8000, debug=True, use_reloader=False)
