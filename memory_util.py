from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationTokenBufferMemory

memory = ConversationBufferWindowMemory(memory_key="chat_history", k=10)

_profile_name = ""


def extract_profile_name(profile_name: str) -> str:
    global _profile_name
    _profile_name = profile_name
    return profile_name


def get_profile_name() -> str:
    # return the profile name from the global variable
    global _profile_name
    return _profile_name
