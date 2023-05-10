from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationTokenBufferMemory

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

_profile_name = ""


def extract_profile_name(profile_name: str) -> str:
    global _profile_name
    _profile_name = profile_name
    return profile_name


def get_profile_name() -> str:
    """

    :rtype: object
    """
    # return the profile name from the global variable
    global _profile_name
    return _profile_name
