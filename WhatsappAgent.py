from dotenv import load_dotenv
from langchain import LLMChain, GoogleSearchAPIWrapper, PromptTemplate
from langchain.agents import Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory
from langchain.utilities import GooglePlacesAPIWrapper

from WebpageScrapper import WebScraper
from memory_util import memory, get_profile_name

# from llama_index.optimization import SentenceEmbeddingOptimizer

load_dotenv()

readonlymemory = ReadOnlySharedMemory(memory=memory)


class WhatsappAgent:
    def getAgent(self):
        agent = ZeroShotAgent(llm_chain=self.getChain(), tools=self.getTools(), verbose=True)
        return agent

    def getChain(self):
        llm = ChatOpenAI(temperature=0)
        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access 
        to the following tools:"""
        suffix = """Begin!"
        
                {chat_history}
               Question: {input}
               {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(
            self.getTools(),
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return llm_chain

    def getTools(self):
        tools = [
            Tool(
                name="General Knowledge Base",
                func=self.getBaseResult,
                description="Use this tool more when you want to answer general question on whide array of topic, which you dont need to search the web for. topic like history, programming, law, general knowledge"
                            "should know about only then search the web",

            ),
            Tool(
                name="Greeting Buddy",
                func=self.getGreetResult,
                description="useful for when you want to greet a human and make them feel welcome and answer based on their input ",
                return_direct=True,


            ),
            Tool(
                name="Google Search API",
                func=self.getGoogleSearchResult,
                description="useful for when you want search the internet to find a fact or information which you don't know about or happened after your knowledge cutoff",
                return_direct=True,


            ),
            Tool(
                name="Google Places API",
                func=self.getGooglePlaceResult,
                description="useful when you want to find the address of a place or a restaurant or a shop or a landmark ",
                return_direct=True,


            ),
            Tool(
                name="Web page summarizer",
                func=self.getWebpageResult,
                description="useful when you want extract the text of a web page and summarize it for the user "
                            "the user will provide the webpage as input",
                return_direct=True,

            ),
            Tool(
                name="Summary",
                func=self.summry_chain.run,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary."
            )
        ]
        return tools

    def getGoogleSearchResult(self, queryString):
        print(f"hello {queryString}")
        search = GoogleSearchAPIWrapper(k=5)
        queryResult = search.run(queryString)
        parseResult = self.getParsedResult(queryString, queryResult)
        return parseResult

    def getGreetResult(self, queryString):
        print(f"hello {queryString}")
        profile_name = "akshay"
        parseResult = self.getParsedGreetResult(queryString, profile_name)
        return parseResult

    def getGooglePlaceResult(self, queryString):
        print(f"hello {queryString}")
        placeSearch = GooglePlacesAPIWrapper(top_k_results=5)
        queryResult = placeSearch.run(queryString)
        parseResult = self.getParsedResult(queryString, queryResult)
        return parseResult

    def getWebpageResult(self, queryString):
        print(f"hello {queryString}")
        webscrapper = WebScraper(queryString)
        webResult = webscrapper.extract_text()
        parseReult = self.getParsedWebResult(queryString, webResult)
        return parseReult

    def getBaseResult(self, queryString):
        # buddy = BuddyChain()
        # chain = buddy.getBaseLLMChain()
        result = self.getKbParsedResult(queryString)
        return result

    def getParsedGreetResult(self, queryString, name):
        print("query",queryString)
        template = """You are greeting assistant that greets humans in one liner and makes them feel welcomed. You 
        are creative in responses and dont extend the greeting to over a sentence. Also remember to use the name of human:
        Name: {name} 
        ===========
        This is the human message to you: {input}"""
        prompt = PromptTemplate(
            input_variables=["input", "name"],
            template=template
        )
        summry_chain = LLMChain(
            llm=ChatOpenAI(),
            prompt=prompt,
            verbose=True,
        )
        parsedResult = summry_chain({"input": queryString, "name": name}, return_only_outputs=True).get('text')
        return parsedResult

    def getParsedResult(self, queryString, queryResult):
        template = """Given the following google result and a question, create a final answer. 
        If you don't know the answer, just say that you don't know. Don't try to make up an answer.

        {chat_history}
        Human: {human_input}
        =========
        {context}
        =========
        Chatbot:"""
        PROMPT = PromptTemplate(template=template, input_variables=["chat_history", "context", "human_input"])
        llm = ChatOpenAI(temperature=0)
        chain = LLMChain(llm=llm, prompt=PROMPT, memory=readonlymemory)
        parsedResult = chain({"context": queryResult, "human_input": queryString}, return_only_outputs=True).get('text')
        return parsedResult

    def getParsedWebResult(self, queryString, queryResult):
        template = """Given the following web page text and a question, create a final answer, also summarize the text 
        for the user if asked. If you don't know the answer, just say that you don't know. Don't try to make up an 
        answer.

        {chat_history}
        Human: {human_input}
        =========
        {context}
        =========
        Chatbot:"""
        PROMPT = PromptTemplate(template=template, input_variables=["chat_history", "context", "human_input"])
        llm = ChatOpenAI(temperature=0)
        chain = LLMChain(llm=llm, prompt=PROMPT, memory=readonlymemory)
        parsedResult = chain({"context": queryResult, "human_input": queryString}, return_only_outputs=True).get('text')
        return parsedResult

    def getKbParsedResult(self, queryString):
        template = """You are an helpful Ai assitant with knowledge on wide variety of subjects and assists in 
        answering user query to best of your ability, if you dont know just say that you don't know. Don't try to 
        make up an answer.
        
        {chat_history}
        Human: {human_input}
        =========
        Chatbot:"""
        PROMPT = PromptTemplate(template=template, input_variables=["chat_history", "human_input"])
        llm = ChatOpenAI(temperature=0)
        chain = LLMChain(llm=llm, prompt=PROMPT, memory=readonlymemory)
        parsedResult = chain({"human_input": queryString}, return_only_outputs=True).get('text')
        return parsedResult

    template = """This is a conversation between a human and a bot:

    {chat_history}

    Write a summary of the conversation for {input}:
    """

    prompt = PromptTemplate(
        input_variables=["input", "chat_history"],
        template=template
    )
    summry_chain = LLMChain(
        llm=ChatOpenAI(),
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )
