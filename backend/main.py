from flask import Flask, request, jsonify
from flask_cors import CORS
from retriever import build_retriever
from tools.search import search_and_scrape_part_details
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools import tool
from retriever import is_deepseek_available
import os

app = Flask(__name__)
CORS(app)

retriever = build_retriever()

# Choose LLM
if is_deepseek_available():
    print("✅ DeepSeek is available")
    llm = ChatDeepSeek(model="deepseek-chat")
else:
    print("⚠️ DeepSeek is not available. Falling back to OpenAI GPT-4")
    llm = ChatOpenAI(model="gpt-4")

# Define tool
search_tool = Tool.from_function(
    name="PartSearchAndScrapeTool",
    func=search_and_scrape_part_details,
    description="Use this tool to find information about a specific part by part number."
)

# Agent
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    # agent_kwargs={
    # "system_message": """
    #     You are a helpful and friendly assistant designed to provide accurate product information and help users with purchasing or troubleshooting appliance parts from PartSelect.com.

    #     You must:
    #     - Focus only on refrigerators and dishwashers.
    #     - Refuse or redirect questions unrelated to PartSelect or those appliances.
    #     - Maintain a calm, respectful, and friendly tone.
    #     - Avoid hallucinating information not on product pages.
    #     - Prefer factual information and offer to help users search or clarify model numbers when needed.
        
    #     When using tools:
    #     - Format your output exactly as follows, with no extra commentary:
    #         Action: ToolName
    #         Action Input: "your input here"
    #     - Do NOT add parentheses, thoughts, or explanation after Action Input.
    #     """
    # }
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
