# # Set up the base template
# from typing import List, Union
# import re
# from dotenv import load_dotenv
# from langchain import LLMChain, SerpAPIWrapper, GoogleSearchAPIWrapper
# from langchain.agents import Tool, AgentOutputParser, LLMSingleActionAgent, AgentExecutor
# from langchain.chains import llm
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import BaseChatPromptTemplate
# from langchain.schema import AgentAction, AgentFinish, HumanMessage
# from langchain.tools import GooglePlacesTool
# from langchain.utilities import GooglePlacesAPIWrapper
#
# load_dotenv()
# placeSearch = GooglePlacesAPIWrapper(top_k_results=5)
# search = GoogleSearchAPIWrapper(k=5)
# template = """Answer the following questions as best you can. You have access to the following tools:
#
# {tools}
#
# Use the following format:
#
# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question
#
# Begin! Remember to speak as a pirate when giving your final answer. Use lots of "Arg"s
#
# Question: {input}
# {agent_scratchpad}"""
#
#
# # Set up a prompt template
# class CustomPromptTemplate(BaseChatPromptTemplate):
#     # The template to use
#     template: str
#     # The list of tools available
#     tools: List[Tool]
#
#     def format_messages(self, **kwargs) -> str:
#         # Get the intermediate steps (AgentAction, Observation tuples)
#         # Format them in a particular way
#         intermediate_steps = kwargs.pop("intermediate_steps")
#         thoughts = ""
#         for action, observation in intermediate_steps:
#             thoughts += action.log
#             thoughts += f"\nObservation: {observation}\nThought: "
#         # Set the agent_scratchpad variable to that value
#         kwargs["agent_scratchpad"] = thoughts
#         # Create a tools variable from the list of tools provided
#         kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
#         # Create a list of tool names for the tools provided
#         kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
#         formatted = self.template.format(**kwargs)
#         return [HumanMessage(content=formatted)]
#
#
#
# class CustomOutputParser(AgentOutputParser):
#
#     def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
#         # Check if agent should finish
#         if "Final Answer:" in llm_output:
#             return AgentFinish(
#                 # Return values is generally always a dictionary with a single `output` key
#                 # It is not recommended to try anything else at the moment :)
#                 return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
#                 log=llm_output,
#             )
#         # Parse out the action and action input
#         regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
#         match = re.search(regex, llm_output, re.DOTALL)
#         if not match:
#             raise ValueError(f"Could not parse LLM output: `{llm_output}`")
#         action = match.group(1).strip()
#         action_input = match.group(2)
#         # Return the action and action input
#         return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
#
#
# def getTools():
#     tools = [
#         Tool(
#             name="Google Search API",
#             func=search.run,
#             description="useful for when you want answer a general qustion or find a fact about something by searching the web",
#             return_direct=True,
#
#         ),
#         Tool(
#             name="Google Places API",
#             func=placeSearch.run,
#             description="useful when you want to find the address of a place or a restaurant or a shop or a landmark ",
#             return_direct=True,
#
#         ),
#     ]
#     return tools
#
#
# def getCustomAgent(query)->str:
#     tools = getTools()
#     prompt = CustomPromptTemplate(
#         template=template,
#         tools=tools,
#         # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
#         # This includes the `intermediate_steps` variable because that is needed
#         input_variables=["input", "intermediate_steps"]
#     )
#     output_parser = CustomOutputParser()
#     tool_names = [tool.name for tool in tools]
#     llm = ChatOpenAI(temperature=0)
#     llm_chain = LLMChain(llm=llm, prompt=prompt)
#     agent = LLMSingleActionAgent(llm_chain=llm_chain,
#                                  output_parser=output_parser,
#                                  stop=["\nObservation:"],
#                                  allowed_tools=tool_names)
#
#     agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
#     return agent_executor.run(query)
