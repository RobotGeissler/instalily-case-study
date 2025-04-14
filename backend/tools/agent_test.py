from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI  # or ChatDeepSeek if using that
from langchain.agents.agent_types import AgentType
from search import search_tool

llm = ChatOpenAI(model="gpt-4")

agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

response = agent.run("Find part number PS11752778 and tell me if it's compatible with WDT780SAEM1.")
print(response)
