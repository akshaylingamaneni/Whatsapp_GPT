import os
from typing import Dict, Any

import openai.error
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import AgentExecutor
from langchain.chains import OpenAIModerationChain
from pydantic import BaseModel

from WhatsappAgent import WhatsappAgent
from memory_util import memory, extract_profile_name
from twilio_whatsapp.TwilioMessenger import TwilioMessenger

# from CustomAgent import getCustomAgent

app = FastAPI()
load_dotenv()

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')

# Retrieve the Twilio auth token from the environment variables
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

# Retrieve the Twilio phone number from the environment variables
from_number = os.environ.get('TWILIO_FROM_NUMBER')


class Query(BaseModel):
    user_query: str
    json_field: Dict[str, Any]


class MessageResponse(BaseModel):
    response: Any
    status: str


@app.get("/")
def root():
    return {"message": "This is the root of the API"}


@app.post("/fetchResponse")
async def query_user(query: Query) -> dict:
    profile_name = query.json_field["ProfileName"]
    to_number = query.json_field["From"]
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
                                                            verbose=True, max_iterations=5,
                                                            early_stopping_method="generate",
                                                            max_execution_time=60,
                                                            memory=memory)
        response = agent_executor.run(query.user_query)
        messenger = TwilioMessenger(account_sid, auth_token, from_number)
        print(to_number)
        messageStatus = await messenger.send_message(to_number, response)
        messageResponse = MessageResponse(response=response, status=messageStatus)
        return messageResponse.dict()
    except openai.error.InvalidRequestError as e:
        print(e)
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
