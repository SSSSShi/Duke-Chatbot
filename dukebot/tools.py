# tools.py
from urllib.parse import quote
from langchain.tools import Tool
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_events_from_duke_api(feed_type="json", future_days=45, groups=['All'], categories=['All'], filter_method_group=True, filter_method_category=True):
    """
    Fetch events from Duke University's public calendar API with optional filters.
    """
    # When feed_type is not one of these types, add the simple feed_type parameter.
    feed_type_param = ""
    if feed_type not in ['rss', 'js', 'ics', 'csv']:
        feed_type_param = "feed_type=simple"
    
    feed_type_url = feed_type_param if feed_type_param else ""
    group_url = ""
    category_url = ""

    if filter_method_group:
        if 'All' in groups:
            group_url = ""
        else:
            for group in groups:
                group_url += '&gfu[]='+quote(group, safe="")
    else:
        if 'All' in groups:
            group_url = ""
        else:
            group_url = "&gf[]=" + quote(groups[0], safe="")
            for group in groups[1:]:
                group_url += "&gf[]=" + quote(group, safe="")

    if filter_method_category:
        if 'All' in categories:
            category_url = ""
        else:
            for category in categories:
                category_url += '&cfu[]=' + quote(category, safe="")
    else:
        if 'All' in categories:
            category_url = ""
        else:
            for category in categories:
                category_url += "&cf[]=" + quote(category, safe="")

    url = f'https://calendar.duke.edu/events/index.{feed_type}?{category_url}{group_url}&future_days={future_days}&{feed_type_url}'

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Try to parse JSON response if feed_type is json
        if feed_type == 'json':
            return json.dumps(response.json())
        return response.text
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to fetch events data: {str(e)}"})
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse response as JSON"})
    

def get_curriculum_with_subject_from_duke_api(subject):
    """
    Retrieve curriculum information from Duke University's API by specifying a subject code.
    """
    subject_url = quote(subject, safe="")

    # Updated with a more reliable access token, if the old one has expired
    # You may need to replace this with a valid token
    url = f'https://streamer.oit.duke.edu/curriculum/courses/subject/{subject_url}?access_token=19d3636f71c152dd13840724a8a48074'

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Try to parse JSON response
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        # Create a more useful error response
        error_data = {
            "error": f"Failed to fetch curriculum data: {str(e)}",
            "status_code": response.status_code if hasattr(response, 'status_code') else None,
            "url": url
        }
        return json.dumps(error_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse response as JSON"})
    
def get_detailed_course_information_from_duke_api(course_id: str, course_offer_number: str):

    """
    
    Retrieve curriculum information from Duke University's API by specifying a course ID and course offer number, allowing you to access detailed information about a specific course.

    Parameters:
        course_id (str): The course ID to get curriculum data for. For example, the course ID is 029248' for General African American Studies.
        course_offer_number (str): The course offer number to get curriculum data for. For example, the course offer number is '1' for General African American Studies.

    Returns:
        str: Raw curriculum data in JSON format or an error message.

    """

    url = f'https://streamer.oit.duke.edu/curriculum/courses/crse_id/{course_id}/crse_offer_nbr/{course_offer_number}'

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch data: {response.status_code}"
    
def get_people_information_from_duke_api(name: str):

    """
    
    Retrieve people information from Duke University's API by specifying a name, allowing you to access detailed information about a specific person.

    Parameters:
        name (str): The name to get people data for. For example, the name is 'John Doe'.

    Returns:
        str: Raw people data in JSON format or an error message.

    """

    name_url = quote(name, safe="")

    url = f'https://streamer.oit.duke.edu/ldap/people?q={name_url}&access_token=19d3636f71c152dd13840724a8a48074'

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch data: {response.status_code}"

def get_pratt_info_from_serpapi(query="Duke Pratt School of Engineering", api_key=None, filter_domain=True):
    """
    Retrieve information about Duke's Pratt School of Engineering using SerpAPI.
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get("SERPAPI_API_KEY")
        if not api_key:
            return json.dumps({"error": "SerpAPI key not found. Please provide an API key or set SERPAPI_API_KEY environment variable."})
    
    # Ensure the query includes Duke Pratt
    if "duke pratt" not in query.lower():
        query = f"Duke Pratt School of Engineering {query}"
    
    # Construct the SerpAPI URL with the query
    encoded_query = quote(query)
    url = f"https://serpapi.com/search.json?q={encoded_query}&engine=google&num=10&api_key={api_key}"
    
    try:
        # Make the request to SerpAPI
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse the JSON response
        search_results = response.json()
        
        # Process and filter the results
        processed_results = process_serpapi_results(search_results, filter_domain)
        
        return json.dumps(processed_results)
        
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to fetch data from SerpAPI: {str(e)}"})
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse SerpAPI response as JSON"})

def process_serpapi_results(search_results, filter_domain=True):
    """
    Process and filter SerpAPI results to extract the most relevant information.
    """
    processed_data = {
        "search_metadata": {},
        "organic_results": [],
        "knowledge_graph": {},
        "related_questions": []
    }
    
    # Extract search metadata
    if "search_metadata" in search_results:
        processed_data["search_metadata"] = {
            "query": search_results["search_metadata"].get("query", ""),
            "total_results": search_results.get("search_information", {}).get("total_results", 0)
        }
    
    # Extract organic results
    if "organic_results" in search_results:
        organic_results = search_results["organic_results"]
        
        # Filter for duke.edu domains if requested
        if filter_domain:
            # More aggressive filtering - require "duke" in the link or snippet
            filtered_results = [result for result in organic_results 
                               if "duke" in result.get("link", "").lower() or 
                                  "duke" in result.get("snippet", "").lower()]
            
            # Further prioritize pratt.duke.edu results
            pratt_results = [result for result in filtered_results 
                            if "pratt.duke.edu" in result.get("link", "")]
            
            other_duke_results = [result for result in filtered_results 
                                 if "pratt.duke.edu" not in result.get("link", "")]
            
            # Combine with pratt results first, then other duke results
            processed_results = pratt_results + other_duke_results
            
            # If we have no results after filtering, use the original results
            if not processed_results and organic_results:
                processed_results = organic_results[:5]  # Just take the top 5
        else:
            processed_results = organic_results
        
        # Extract the most useful information from each result
        for result in processed_results[:8]:  # Limit to top 8 results
            processed_data["organic_results"].append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("source", "")
            })
    
    # Extract knowledge graph information if available
    if "knowledge_graph" in search_results:
        kg = search_results["knowledge_graph"]
        processed_data["knowledge_graph"] = {
            "title": kg.get("title", ""),
            "type": kg.get("type", ""),
            "description": kg.get("description", ""),
            "website": kg.get("website", ""),
            "address": kg.get("address", "")
        }
    
    # Extract related questions if available
    if "related_questions" in search_results:
        for question in search_results["related_questions"][:4]:  # Limit to top 4 questions
            processed_data["related_questions"].append({
                "question": question.get("question", ""),
                "answer": question.get("answer", "")
            })
    
    return processed_data

def get_specific_pratt_info(topic="general", subtopic=None, api_key="9339dbe03e129628964af59694c4709f334ee7bf84e7c0c1e335cbc9ea0bbaf6"):
    """
    Retrieve specific information about Duke's Pratt School of Engineering using SerpAPI.
    """
    # Map topics to specific search queries
    topic_queries = {
        "general": "Duke Pratt School of Engineering overview information",
        "academics": "Duke Pratt School of Engineering academic programs degrees majors",
        "admissions": "Duke Pratt School of Engineering admissions requirements application deadlines",
        "ai_meng": "Duke Pratt AI for Product Innovation MEng program curriculum courses",
        "student_life": "Duke Pratt School of Engineering student life experience campus",
        "research": "Duke Pratt School of Engineering research areas labs projects",
        "faculty": "Duke Pratt School of Engineering faculty professors researchers",
        "events": "Duke Pratt School of Engineering events workshops seminars"
    }
    
    # Map subtopics for more specific queries
    subtopic_queries = {
        "academics": {
            "undergraduate": "Duke Pratt School of Engineering undergraduate programs BSE degrees majors",
            "graduate": "Duke Pratt School of Engineering graduate programs masters PhD",
            "courses": "Duke Pratt School of Engineering course offerings classes",
            "requirements": "Duke Pratt School of Engineering degree requirements curriculum"
        },
        "admissions": {
            "undergraduate": "Duke Pratt School of Engineering undergraduate admissions requirements deadlines",
            "graduate": "Duke Pratt School of Engineering graduate admissions requirements deadlines",
            "deadlines": "Duke Pratt School of Engineering application deadlines",
            "requirements": "Duke Pratt School of Engineering application requirements"
        },
        "ai_meng": {
            "curriculum": "Duke Pratt AI for Product Innovation MEng program curriculum courses",
            "admissions": "Duke Pratt AI for Product Innovation MEng program admissions requirements",
            "careers": "Duke Pratt AI for Product Innovation MEng program career outcomes jobs",
            "faculty": "Duke Pratt AI for Product Innovation MEng program faculty instructors"
        }
    }
    
    # Check if the topic is valid
    if topic not in topic_queries:
        return json.dumps({
            "error": f"Topic '{topic}' not found",
            "available_topics": list(topic_queries.keys())
        })
    
    # Construct the query based on topic and subtopic
    if subtopic and topic in subtopic_queries and subtopic in subtopic_queries[topic]:
        query = subtopic_queries[topic][subtopic]
    else:
        query = topic_queries[topic]
    
    # Call the SerpAPI search function
    return get_pratt_info_from_serpapi(query, api_key)

# Wrap these functions into LangChain Tools
tools = [
    Tool(
        name="get_duke_events",
        func=get_events_from_duke_api,
        description=(
            "Use this tool to retrieve upcoming events from Duke University's calendar via Duke's public API. "
            "You can specify the format of the returned data (e.g., 'rss', 'js', 'ics', 'csv', 'json', 'jsonp') "
            "and the number of days into the future to fetch events. You can also filter by groups and categories: "
            "groups are the organizer or host groups of the events, while categories are the thematic or topical category of the events."
            "set filter_method_group=True to require that an event match ALL specified groups (AND), or False to "
            "match ANY of them (OR). Similarly, set filter_method_category=True for an AND filter on categories, "
            "or False for an OR filter. Using ['All'] for either groups or categories fetches events without "
            "filtering on that parameter. The function returns raw calendar data or an error message."
            "Parameters:"
            "   feed_type (str): Format of the returned data. Acceptable values include 'rss', 'js', 'ics', 'csv', 'json', 'jsonp'."
            "   future_days (int): Number of days into the future for which to fetch events. Defaults to 45."
            "   groups (list): List of groups to filter events by. Use ['All'] to include events from all groups."
            "   categories (list): List of categories to filter events by. Use ['All'] to include events from all categories."
            "   filter_method_group (bool): True: Event must match ALL specified groups (AND). False: Event may match ANY of the specified groups (OR)."
            "   filter_method_category (bool): True: Event must match ALL specified categories (AND). False: Event may match ANY of the specified categories (OR)."
        )
    ),
    Tool(
        name="get_curriculum_with_subject_from_duke_api",
        func=get_curriculum_with_subject_from_duke_api,
        description=(
            "Use this tool to retrieve curriculum information from Duke University's API."
            "Retrieve curriculum information from Duke University's API by specifying a subject code, allowing you to access brief details about available courses."
            "It returns a JSON object with brief details about available courses, including course IDs and offer numbers."
            "Parameters:"
            "   subject (str): The subject to get curriculum data for. For example, the subject is 'ARABIC-Arabic'."
            "Return:"
            "   str: Raw curriculum data in JSON format or an error message. If valid result, the response will contain each course's course id and course offer number for further queries."
        )
    ),
    Tool(
        name="get_detailed_course_information_from_duke_api",
        func=get_detailed_course_information_from_duke_api,
        description=(
            "Use this tool to retrieve detailed curriculum information from Duke University's API."
            "Retrieve curriculum information from Duke University's API by specifying a course ID and course offer number, allowing you to access detailed information about a specific course."
            "The course ID and course offer number can be obtained from the previous tool."
            "It returns a JSON object with detailed information about the course."
            "Parameters:"
            "   course_id (str): The course ID to get curriculum data for. For example, the course ID is 029248' for General African American Studies."
            "   course_offer_number (str): The course offer number to get curriculum data for. For example, the course offer number is '1' for General African American Studies."
            "Return:"
            "   str: Raw curriculum data in JSON format or an error message."
        )
    ),
    Tool(
        name="get_people_information_from_duke_api",
        func=get_people_information_from_duke_api,
        description=(
            "Use this tool to retrieve people information from Duke University's API."
            "Retrieve people information from Duke University's API by specifying a name, allowing you to access detailed information about a specific person."
            "It returns a JSON object with detailed information about the person."
            "Parameters:"
            "   name (str): The name to get people data for. For example, the name is 'Brinnae Bent'."
            "Return:"
            "   str: Raw people data in JSON format or an error message."
        )
    ),
    Tool(
        name="get_pratt_info_serpapi",
        func=get_specific_pratt_info,
        description=(
            "Use this tool to retrieve information about Duke University's Pratt School of Engineering using SerpAPI. "
            "You can specify a topic (general, academics, admissions, ai_meng, student_life, research, faculty, events) "
            "and optionally a subtopic for more specific information. "
            "Parameters: "
            "  topic (str): The specific topic to search for information about. "
            "  subtopic (str, optional): A more specific aspect of the topic to focus on. "
            "  api_key (str): Your SerpAPI API key. "
            "The tool returns JSON-formatted search results from SerpAPI about the specified Pratt topic."
        )
    )
]
