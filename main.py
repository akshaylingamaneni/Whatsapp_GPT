from typing import Dict, Any

import openai.error
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chains import OpenAIModerationChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.tools import GooglePlacesTool
from langchain.agents import AgentExecutor
from pydantic import BaseModel, Json
from memory_util import memory, extract_profile_name
from WhatsappAgent import WhatsappAgent
# from CustomAgent import getCustomAgent

app = FastAPI()
load_dotenv()
class Query(BaseModel):
    user_query: str
    json_field: Dict[str, Any]


@app.get("/")
def root():
    return {"message": "This is the root of the API"}


@app.post("/fetchResponse")
async def query_user(query: Query) -> dict:
    profile_name = query.json_field["ProfileName"]
    extract_profile_name(profile_name)
    custom_moderation = CustomModeration()
    result = custom_moderation.run(query.user_query)
    if not result:
        return {"response": "Sorry, I cannot answer that question. As it violates my content policy. Please refrain "
                            "from asking hate, self-harm, violence and graphic questions. If you continue to ask "
                            "these questions, your account will be flagged and I wont be able to assist you."}
    try:
        agent = WhatsappAgent()
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent.getAgent(), tools=agent.getTools(),
                                                            verbose=True, max_iterations=1,
                                                            early_stopping_method="generate",
                                                            max_execution_time=10,
                                                            memory=memory)
        response = agent_executor.run(query.user_query)
        return {"response": response}
    except openai.error.InvalidRequestError as e:
        memory.clear()
        return {"response": "Sorry, think I am hallucinating. Please try again later."}
        pass
    except Exception as e:
        print(e)
        return {"response": "Sorry, I am having trouble answering your question. Please try again later."}


class CustomModeration(OpenAIModerationChain):

    def _moderate(self, text: str, results: dict) -> bool:
        if results["flagged"]:
            error_str = f"The following text was found that violates OpenAI's content policy: {text}"
            return False
        return True
