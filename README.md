[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/oqjgKq0J)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=19023621)

## Duke Chatbot
    
A Duke Chatbot project built with LangChain that integrates with Duke University's APIs to provide information about campus events, course curricula, people, and related Duke Pratt School of Engineering details.   

### Features   

- Event Retrieval: Get upcoming Duke events using natural language queries.
- Curriculum & Course Info: Fetch curriculum data and detailed course information by subject or course IDs.
- People Information: Retrieve information about Duke personnel from the Duke API.
- Advanced Query Handling: Leverages fuzzy matching and search tools for accurate subject, group, and category formatting.
- SerpAPI Integration: Uses SerpAPI to obtain Duke Pratt School of Engineering related details.
- Conversational Memory: Maintains conversation context using LangChain’s memory modules.

### Installation and Run

**Clone the Repository:**

`git clone https://your.repo.url/duke-chatbot.git`   

**Install Dependencies**

`pip install -r requirements.txt`
 
**Configure Environment Variables**   
Create a .env file in the root directory with:    

`OPENAI_API_KEY=your_openai_api_key`
`SERPAPI_API_KEY=your_serpapi_api_key`

**Run the chatbot with some test queries**

`python agent.py`

**Project Structure**  

Duke Chatbot Project/    
├── dukebot/     
│   ├── __init__.py   
│   ├── tools.py    
│   └── agent.py    
├── evaluation/       
│   ├── __init__.py    
│   └── eval.py    
└── resources/     
│    ├── groups.txt   
│    ├── categories.txt     
│    └── subjects.txt    

