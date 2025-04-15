from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI  # Correct import
from langchain.memory import ConversationBufferMemory  # Correct import
from langchain_core.tools import Tool
import os
import json
from dotenv import load_dotenv

# Import your custom tools from tools.py
from tools import (
    get_events_from_duke_api,
    get_curriculum_with_subject_from_duke_api,
    get_detailed_course_information_from_duke_api,
    get_people_information_from_duke_api,
    get_pratt_info_from_serpapi
)

# Load environment variables from .env file
load_dotenv()

def create_duke_agent():
    """
    Create a LangChain agent with the Duke tools.
    API keys are loaded from .env file.
    
    Returns:
        An initialized LangChain agent
    """
    # Get API keys from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    
    # Check if API keys are available
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not serpapi_api_key:
        raise ValueError("SERPAPI_API_KEY not found in environment variables")
    
    # Define your tools with the API keys - FIXED TOOL DEFINITIONS
    tools = [
        Tool(
            name="DukeEvents",
            func=get_events_from_duke_api,  # No lambda, use the function directly
            description=(
                "Use this tool to retrieve upcoming events from Duke University's calendar. "
                "You can specify format, days, groups, and categories."
            )
        ),
        Tool(
            name="DukeCurriculum",
            func=get_curriculum_with_subject_from_duke_api,
            description=(
                "Use this tool to retrieve curriculum information by specifying a subject code. "
                "Example subject: 'COMPSCI-Computer Science'."
            )
        ),
        Tool(
            name="DukeDetailedCourse",
            func=get_detailed_course_information_from_duke_api,
            description=(
                "Use this tool to retrieve detailed curriculum information by specifying a course ID and course offer number."
            )
        ),
        Tool(
            name="DukePeople",
            func=get_people_information_from_duke_api,
            description=(
                "Use this tool to retrieve information about Duke people by specifying a name."
            )
        ),
        Tool(
            name="PrattSearch",
            func=lambda query: get_pratt_info_from_serpapi(
                query="Duke Pratt School of Engineering " + query,  # Force Duke Pratt in the query
                api_key=serpapi_api_key,
                filter_domain=True  # Ensure we filter for Duke domains
            ),
            description=(
                "Use this tool to search for information about Duke Pratt School of Engineering. "
                "Specify your search query."
            )
        ),
        # Tool(
        #     name="ScrapePrattLink",
        #     func=get_specific_link_info,
        #     description=(
        #         "Use this tool to scrape and extract detailed information from a specific URL about Duke Pratt."
        #     )
        # ),
        # Tool(
        #     name="PrattSearchAndFollow",
        #     func=lambda query: get_pratt_serp_then_follow_link(
        #         query="Duke Pratt School of Engineering " + query,
        #         link_index=0,
        #         api_key=serpapi_api_key
        #     ),
        #     description=(
        #         "Use this tool to search for Pratt information and automatically follow the most relevant link for details."
        #     )
        # )
    ]
    
    # Create a memory instance
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Initialize the LLM with the OpenAI API key
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model_name="gpt-4",
        temperature=0
    )
    
    # Initialize the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory
    )
    
    return agent

# Modified function to process user queries
def process_user_query(query):
    try:
        # Create the agent
        duke_agent = create_duke_agent()
        
        # Process the query using invoke instead of run (addressing the deprecation warning)
        response = duke_agent.invoke({"input": query})
        
        # Extract the agent's response
        return response.get("output", "I couldn't process your request at this time.")
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return f"An error occurred: {str(e)}"

# Example usage
def main():
    # Test queries
    test_queries = [
        "What events are happening at Duke this week?",
        "Get me detailed information about the course 'COMPSCI 101' with course offer number '1'"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = process_user_query(query)
        print(f"Response: {response}")
        print("-" * 80)

if __name__ == "__main__":
    main()


# example cases:
# "Tell me about the AI MEng program at Duke Pratt"
# "Get me the upcoming events at Duke University"
# "Get me the curriculum for Computer Science"
# "Get me detailed information about the course 'COMPSCI 101' with course offer number '1'"
# "Get me the latest news about Duke Pratt School of Engineering"
# "What are the admission requirements for Duke Pratt?"