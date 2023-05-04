from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate


class BuddyChain:
    def getBasePromptTemplate(self):
        template = """You are a helpful ai assistant that who has knowledge on wide range of topics and you are 
        caring and compassionate and you will answer any question that the user might have and you will be 
        responsible for providing the user with the answers to their queries. If you don't know, say you don't know"""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        return chat_prompt

    def getBaseLLMChain(self):
        llm = ChatOpenAI(temperature=0)
        prompt = self.getBasePromptTemplate()
        base_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,  # use the read-only memory to prevent the tool from modifying the memory
        )
        return base_chain

# kb = UpscKbChain()
# chain = kb.getBaseLLMChain()
# print(chain("what is upsc").get("text"))