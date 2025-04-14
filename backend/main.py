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
    verbose=True
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
    app.run(port=8000, debug=True, use_reloader=False)
