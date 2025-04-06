# tools.py
from urllib.parse import quote
from langchain.tools import Tool
import requests

def get_events_from_duke_api(feed_type: str = "json",
                             future_days: int = 45,
                             groups: list = ['All'],
                             categories: list = ['All'],
                             filter_method_group: bool = True,
                             filter_method_category: bool = True) -> str:
    """
    Fetch events from Duke University's public calendar API with optional filters.

    Parameters:
        feed_type (str): Format of the returned data. Acceptable values include:
                         'rss', 'js', 'ics', 'csv', 'json', 'jsonp'. Defaults to 'json'.
        future_days (int): Number of days into the future for which to fetch events.
                           Defaults to 45.
        groups (list):  The organizer or host groups of the events or the related groups in events. For example,
                        '+DataScience (+DS)' refers to events hosted by the DataScience program.
                        Use 'All' to include events from all groups. 
        categories (list): 
                        The thematic or topical category of the events. For example,
                        'Academic Calendar Dates', 'Alumni/Reunion', or 'Artificial Intelligence'.
                         Use 'All' to include events from all categories.
        filter_method_group (bool): 
            - True: Event must match ALL specified groups (AND).
            - False: Event may match ANY of the specified groups (OR).
        filter_method_category (bool): 
            - True: Event must match ALL specified categories (AND).
            - False: Event may match ANY of the specified categories (OR).

    Returns:
        str: Raw calendar data (e.g., in JSON, XML, or ICS format) or an error message.
    """
    
    # When feed_type is not one of these types, add the simple feed_type parameter.
    feed_type_param = ""
    if feed_type not in ['rss', 'js', 'ics', 'csv']:
        feed_type_param = "feed_type=simple"
    
    feed_type_url = feed_type_param if feed_type_param else ""

    if filter_method_group:
        if 'All' in groups:
            group_url = ""
        else:
            for group in groups:
                group_url+='&gfu[]='+quote(group, safe="")
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

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch data: {response.status_code}"

def get_curriculum_with_subject_from_duke_api(subject: str):

    """

    Retrieve curriculum information from Duke University's API by specifying a subject code, allowing you to access brief details about available courses.

    Parameters:
        subject (str): The subject to get curriculumn data for. For example, the subject is 'ARABIC-Arabic'.

    Returns:
        str: Raw curriculum data in JSON format or an error message. If valid result, the response will contain each course's course id and course offer number for further queries.
        The value of course id is the value of 'crse_id' in the response, and the value of course offer number is the value of 'crse_offer_nbr' in the response.
    """

    subject_url = quote(subject, safe="")

    url = f'https://streamer.oit.duke.edu/curriculum/courses/subject/{subject_url}?access_token=19d3636f71c152dd13840724a8a48074'

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch data: {response.status_code}"
    
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
        description={
            "Use this tool to retrieve detailed curriculum information from Duke University's API."
            "Retrieve curriculum information from Duke University's API by specifying a course ID and course offer number, allowing you to access detailed information about a specific course."
            "The course ID and course offer number can be obtained from the previous tool."
            "It returns a JSON object with detailed information about the course."
            "Parameters:"
            "   course_id (str): The course ID to get curriculum data for. For example, the course ID is 029248' for General African American Studies."
            "   course_offer_number (str): The course offer number to get curriculum data for. For example, the course offer number is '1' for General African American Studies."
            "Return:"
            "   str: Raw curriculum data in JSON format or an error message."
        }
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
    )
]
