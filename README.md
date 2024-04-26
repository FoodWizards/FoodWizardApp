# FoodWizardApp
A culinary companion empowered by AI to elevate your cooking with top-notch recipe
<img width="1061" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/d27fe38d-fc4e-43e9-bda1-8a3e5d1ab265">

### Project Overview:
### Scope:

FoodWizard is a platform designed to simplify recipe discovery and recommendation. It offers two key functionalities: YouTube video summarization and personalized recipe recommendations based on user preferences.


### Functionalities:

1. **Chrome Extension for Recipe Collection**: 
   - Users can save their favorite cooking tutorial videos from YouTube by inputting the video links.
   - Saved videos are organized into a personalized recipe collection for each user.

2. **YouTube Video Summarization with FoodWizard**: 
   - Utilizes FoodWizard, powered by OpenAI's technology, to extract content from cooking tutorials available in various languages such as Hindi, Tamil, Marathi, and English.

3. **Recipe Recommendations**: 
   - Users can input any text, including specific instructions or preferences, and receive personalized recipe recommendations based on their input.

4. **Recipe Filtering**: 
   - Allows users to filter and search through the listed recipes, making it easier to find recipes based on their preferences and dietary requirements.



### Stakeholders:
The end users for FoodWizard include:
Cooking enthusiasts seeking recipe inspiration and guidance.
Individuals with dietary restrictions or specific flavor preferences looking for tailored recipe recommendations.
Those interested in leveraging technology to simplify their culinary journey and explore new dishes.

### CodeLab: https://codelabs-preview.appspot.com/?file_id=1T4FIak6iigOSCrGLP44bsKpyt_S_kZ1uKInPsoNiBUM#0

### Architecture Diagram:



### Methodology: 




<img width="609" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/e7bb1bfd-63c5-4514-b2c4-6c9538990d4c">

**User authenticates with Google Sign-in:** The user clicks on the Google Sign-in button on the Chrome extension. This redirects the user to a Google authorization page where they can sign in with their Google account.

**User enters Youtube URL:** Once the user has successfully signed in with Google, they can then enter a Youtube URL into the Chrome extension.

**Chrome extension captures Youtube URL:** The Chrome extension captures the Youtube URL that the user has entered.

**Chrome extension sends Youtube URL to backend server:** The Chrome extension sends the captured Youtube URL to the backend server built with FastAPI.

**FastAPI server saves Youtube URL to Snowflake database:** The FastAPI server receives the Youtube URL from the Chrome extension. The FastAPI server then connects to the Snowflake database and saves the Youtube URL for the specific user who is currently signed in.





<img width="1245" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/c52eee50-ac02-47d9-a253-9b857a03b0a3">

**User can Reviews Saved URLs in App:**

**Accessing Saved URLs:** Users can access the app to view a list of their saved YouTube URLs.

**Retrieving Saved URLs:** This list retrieves the URLs previously stored for the user in Snowflake.

**URL Sent to Processing Pipeline (Optional):**
Selection Process: Within the app (optional), users can select a YouTube URL from their list.
Sending to Pipeline: Upon selection (optional), the chosen URL is sent to a message queue like Kafka.

**Processing Pipeline :**
Receiving and Processing: A worker subscribed to the Kafka message queue receives the YouTube URL.
Downloading and Conversion: This worker downloads the video from YouTube and converts it to text using OpenAI Whisper, supporting languages like Hindi, Marathi, Tamil, and English.

Summarization with GPT-3.5: The converted text is sent to OpenAI GPT-3.5 for summarization in a proper format.
Storage or Return: The generated summary can be stored or returned to the user through an API.



<img width="884" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/c5873c80-6106-4881-aaf6-119de95fbbf1">


**Data Collection:**
Source Websites: Recipes were scraped from Archana's Kitchen and Ranveer Brar websites.
Scraping Process:Over 9000 recipes were extracted using Scrapy from these sources.

**Data Cleaning and Validation:**
cleaning Procedures: The collected data underwent thorough cleaning and validation using pydantic to ensure accuracy and consistency.

**Storage:** Cleaned and validated data was stored in Snowflake.

**Embedding Creation:**
Utilizing OpenAI Embeddings:Embeddings for the recipes were generated using OpenAI embeddings technology.
Storage in Pinecone: These embeddings were stored in the Pinecone database for efficient retrieval and processing.

**Pipeline Automation with Airflow:**
Airflow Implementation: The entire pipeline, from data collection to embedding creation, was automated using Apache Airflow.

<img width="908" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/6dfb6c52-9854-4d84-9e39-8517705e1918">

**Deployment:**
Containerization with Docker:  The application is containerized using Docker to ensure consistency and portability across different environments.
Deployment on Google Cloud Platform (GCP): The containerized application is deployed on GCP for scalability and reliability, leveraging the platform's robust infrastructure and services.

**Testing:**
Unit Testing and Integration Testing:Unit testing is implemented to validate the functionality of individual components within the application. Integration testing is conducted to ensure seamless interaction between different components.
Project Journey Documentation on Codelabs: The project's journey is meticulously documented on Codelabs, providing insights into its architecture, utilised services, challenges encountered, and solutions implemented.

**Video Demo:**
Concise and Informative Demonstration:A concise, informative 10-minute video is created to demonstrate the key features and functionalities of the application.



### Resources and Team:

**Technology Stack:**
- API Development: FastAPI (for building the backend API)
- Natural Language Processing (NLP): OpenAI
- Whisper (for multilingual speech recognition of YouTube videos)
- GPT-3.5 Turbo (for large language model tasks like recipe summarization and embedding generation)
- Embeddings API (for storing recipe data in an efficient format)
- Data Storage:
- Snowflake (for storing structured recipe data)
- Pinecone (for storing recipe embeddings for efficient retrieval)
- User Interface: Streamlit (for creating a user-friendly web interface)
- Pipeline Orchestration: Apache Airflow (for automating data processing tasks)
- Web Scraping: Python libraries (Requests, Scrapy, BeautifulSoup)
- Deployment: Docker (for containerization)
- Cloud Platform: Google Cloud Platform (GCP) (for deployment and scaling)

## How to run application 

#### Creating Virtual Environment
1. Create a virtual environment using the command `python -m venv <name of virtual env>`. 
2. Install dependencies required to run the project using `pip install -r path/to/requirements.txt`
3. Activate created virtual env by running `source <name of virtual env>/bin/activate`


##### How to run
1. Create virtual environment and activate it
2. create a .env file to add the credentials required to connect with snowflake, Pinecone API Key, and OpenAI API Key. The required fields are the following
- AIRFLOW_UID=AIRFLOW_UID
- AIRFLOW_PROJ_DIR=AIRFLOW_PROJ_DIR
- SNOWFLAKE_USER = SNOWFLAKE_USER 
- SNOWFLAKE_PASSWORD =SNOWFLAKE_PASSWORD
- SNOWFLAKE_ACCOUNT = SNOWFLAKE_ACCOUNT
- SQLALCHEMY_SILENCE_UBER_WARNING=1
- SNOWFLAKE_TABLE = SNOWFLAKE_TABLE
- SNOWFLAKE_TABLE_VIDEO = SNOWFLAKE_TABLE_VIDEO
- SNOWFLAKE_SCHEMA = SNOWFLAKE_SCHEMA
- SQLALCHEMY_SILENCE_UBER_WARNING=1 
- SNOWFLAKE_DATABASE = SNOWFLAKE_DATABASE
- SNOWFLAKE_WAREHOUSE = SNOWFLAKE_WAREHOUSE
- PINECONE_API_KEY = PINECONE_API_KEY
- OPENAI_API_KEY = OPENAI_API_KEY 
- BASE_URL = BASE_URL

3.Docker


##### How to run

```sh
 docker compose build
 docker compose up
```



## References




2. External Libraries and Dependencies:
   - OpenAI's Python client library (openai-python v0.18.0): Used for interacting with OpenAI's APIs for natural language processing tasks.

3. Data Sources:
   - YouTube: A video-sharing platform where users can find cooking tutorial videos.
   - Archana's kitchen and Ranveer Brar: A comprehensive database of recipes and cooking-related content.
     https://www.archanaskitchen.com/  
     https://ranveerbrar.com/
          

## Documentation and References:
   - FastAPI Documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
   - OpenAI API Documentation: [https://beta.openai.com/docs/](https://beta.openai.com/docs/)
   - Snowflake Documentation: [https://docs.snowflake.com/en/user-guide-intro.html](https://docs.snowflake.com/en/user-guide-intro.html)
   - Docker Documentation: [https://docs.docker.com/](https://docs.docker.com/)
   - GCP Documentation:[https://cloud.google.com/](https://cloud.google.com/docs/)
   - Streamlit Documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)
   - Apache Airflow Documentation: [https://airflow.apache.org/docs/apache-airflow/stable/index.html](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
   - Pydantic Documentation: [https://pydantic-docs.helpmanual.io/](https://pydantic-docs.helpmanual.io/)
   - Pinecone Documentation: [https://www.pinecone.io/](https://www.pinecone.io/)

These resources provide comprehensive documentation, tutorials, and references for the tools, technologies, and libraries used in the project, aiding in the development and understanding of FoodWizard.

## Team Information and Contribution

| Name | Contribution % | Contribution |
| --- | --- | --- |
Asawari Kadam | 33.33% | Create chrome extension , Backend - Fast API , Frontend - Streamlit |
Hariharan Sundaram | 33.33%  | Video processing pipeline - Airflow, CI Integration, Docker |
Rutuja Kute | 33.33%  |Webscraping pipeline , Application testing, Deployment|

