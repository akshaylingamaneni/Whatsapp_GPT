from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools import AIPluginTool
load_dotenv()
tool = AIPluginTool.from_plugin_url("https://www.klarna.com/.well-known/ai-plugin.json")

llm = ChatOpenAI(temperature=0)
tools = load_tools(["requests_all"] )
tools += [tool]

agent_chain = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent_chain.run("find me the cheapest ps5 on klarna link and price?")

