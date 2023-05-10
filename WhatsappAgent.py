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
        agent = ZeroShotAgent(llm_chain=self.getChain(), tools=self.getTools(), verbose=True, stop=["\nObservation:"], )
        return agent

    def getChain(self):
        llm = ChatOpenAI(temperature=0)
        prefix = """You are a intelligent personal assistant Skuzie. You are caring and supportive companion and extremely polite, empathetic, intelligent, answer your masters question from your vast knowledge while not violating your moderation rules. Dont You have access 
                    to the following tools:
                    
                    Use the following format:
                    
                    Question: the input question you must answer
                    Think: can my knowledge answer this question or should I use a tool
                    Action: the action to take, try using your knowledge if you dont know answer using one of tools, but first should use my knowledge to try to answer
                    Action Input: the input to the action along with the user query
                    Observation: the result of the action
                    ... (this Thought/Action/Action Input/Observation can repeat N times only if the query is not answered)
                    Thought: I know the observation, I need to respond back in a professional way
                    Final Answer: the final answer to the original input question
                    """
        suffix = """Begin!"
        
                {chat_history}
               Question: {input}
               {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(
            tools=self.getTools(),
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return llm_chain

    def getTools(self):
        tools = [
            Tool(
                name="Personal Assistant",
                func=self.getBaseResult,
                description="Use this tool more when you want assist with a wide range of tasks, find a fact or information, from answering questions to providing in-depth explanations to providing coding solutions and discussions on a wide range of topics",
            ),
            Tool(
                name="Google Search API",
                func=self.getGoogleSearchResult,
                description="useful for when you want search the internet to find a fact or information which you don't know about or happened after your knowledge cutoff",

            ),
            Tool(
                name="Google Places API",
                func=self.getGooglePlaceResult,
                description="useful when you want to find the address of a place or a restaurant or a shop or a landmark",
                return_direct = True

            ),
            Tool(
                name="Web page summarizer",
                func=self.getWebpageResult,
                description="useful when you want extract the text of a web page and summarize it for the user "
                            "the user will provide the webpage url as input",

            ),
            Tool(
                name="Summary",
                func=self.getConversationSummary,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary.",
            )
        ]
        return tools

    def getGoogleSearchResult(self, queryString):
        print(f"hello {queryString}")
        search = GoogleSearchAPIWrapper(k=3)
        queryResult = search.run(queryString)
        parseResult = self.getParsedResult(queryString, queryResult)
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

    def getParsedResult(self, queryString, queryResult):
        template = """Given the following google result and a question, create a final answer . 
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
        template = """Given the following web page text and a question, answer any question the user might have and 
        and answer the question, also summarize the text for the user if asked. If you don't know the answer, 
        just say that you don't know. Don't try to make up an answer.

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
        template = """You are a personal assistant named {bot_name}.

                    You are is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics and aslo as a programming assitant. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
                    
                    You are is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
                    
                    Overall, you are a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
                    
                    Also remember to use the name of human when greeting: {name}  and tell your master your name {bot_name}. 
                    
                    Your job is done once you have answered the user query, dont do anything additional thinking.
                    
                    {chat_history}
                    Human: {human_input}
                    Assistant:"""
        name = get_profile_name()
        tool_names = "google,places,websearch"
        PROMPT = PromptTemplate(template=template, input_variables=["chat_history", "human_input", "name", "bot_name"])
        llm = ChatOpenAI(temperature=0)
        chain = LLMChain(llm=llm, prompt=PROMPT, memory=readonlymemory)
        parsedResult = chain({"human_input": queryString, "name": name, "bot_name": "Skuzie", "tool_names": tool_names},
                             return_only_outputs=True).get('text')
        return parsedResult

    def getConversationSummary(self, queryString):
        template = """This is a conversation between a human and a bot:

            {chat_history}

            Write a summary of the conversation for {input}:
            """

        prompt = PromptTemplate(
            input_variables=["input", "chat_history"],
            template=template
        )
        summary_chain = LLMChain(
            llm=ChatOpenAI(),
            prompt=prompt,
            verbose=True,
            memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
        )
        summaryResponse = summary_chain({"input": queryString}, return_only_outputs=True).get('text')
        return summaryResponse
