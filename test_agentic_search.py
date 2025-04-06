# agent.py

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools import tools
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Fetch the key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Custom system message to outline the reasoning process:
custom_system_message = (
    "You are a helpful assistant who answers questions about Duke University. "
    "When given a question, follow these steps:\n"
    "1. Restate the question in your own words.\n"
    "2. Plan the steps required to answer (including which tools to use).\n"
    "3. Execute the necessary tool calls.\n"
    "4. Synthesize a final, detailed answer.\n"
    "Keep your chain-of-thought hidden from the user."
)

def run_duke_agent(user_input: str) -> str:
    """
    Runs a ReAct agent that can plan how to use the Duke tools
    to provide an enriched final answer.
    """
    # 1. Create an LLM
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openai_api_key
    )

    # 2. Initialize a ReAct agent
    #    - ZERO_SHOT_REACT_DESCRIPTION: 
    #      The model will 'think aloud' (chain-of-thought internally) 
    #      and decide which tool(s) to use in a multi-step approach.
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,  # set True for debugging; False to hide chain-of-thought in production
        system_message=custom_system_message
    )

    # 3. Let the agent handle the user query
    return agent.run(user_input)

if __name__ == "__main__":
    run_duke_agent("What is Duke’s AI MEng program like, and are there any events this month relevant to prospective students?")