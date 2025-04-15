from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI  # or ChatDeepSeek if using that
from langchain.agents.agent_types import AgentType
from search import search_tool
from advanced_search import advanced_search_tool

llm = ChatOpenAI(model="gpt-4")

agent = initialize_agent(
    tools=[advanced_search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

response = agent.run("Find part number PS11752778 and tell me if it's compatible with WDT780SAEM1.")
print(response)
response = agent.run("Is this part compatible with my WDT780SAEM1 model?")
print(response)
response = agent.run("The ice maker on my Whirlpool fridge is not working. How can I fix it?")
print(response)
