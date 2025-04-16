from google import genai
from dotenv import load_dotenv, find_dotenv
from dukebot.agent import process_user_query
import os

load_dotenv(find_dotenv())

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompts = ["Tell me about the AI MEng program at Duke Pratt",
        "Get me detailed information about the AIPI courses",
        "Tell me about Computer Science classes",
        "Are there any AI events at Duke?",
        "What cs courses are available?",
        "Tell me about the MEng AIPI program"]

for prompt in prompts:
    response = process_user_query(prompt)

    judge_response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents="You are an expert judge evaluating the quality of AI-generated answers. " \
        "Grade the responses using the following categories out of 5 and use parenthesis to indicate the grade in this format (x/5) where x is the grade: helpfulness, relevance, coherence, and completeness." \
        f'Prompt given to LLM: {prompt}' \
        f'Response from LLM: {response}'
    )
    print(judge_response.text)
    split = judge_response.text.split('/')
    helpfulness = split[0][-1]
    relevance = split[1][-1]
    coherence = split[2][-1]
    completeness = split[3][-1]
    grade = (int(helpfulness) + int(relevance) + int(coherence) + int(completeness)) / 4
    print(f'Overall Grade: {grade / 5 * 100}%')