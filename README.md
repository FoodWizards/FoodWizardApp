# FoodWizardApp
A culinary companion empowered by AI to elevate your cooking with top-notch recipe
<img width="1061" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/d27fe38d-fc4e-43e9-bda1-8a3e5d1ab265">

Project Overview:
Scope:

FoodWizard is a platform designed to simplify recipe discovery and recommendation. It offers two key functionalities: YouTube video summarization and personalized recipe recommendations based on user preferences.

Functionalities:
YouTube Video Summarization:
Users input YouTube video links of cooking tutorials.
FoodWizard extracts and summarizes recipe content using OpenAI.
Users can specify parameters like difficulty level and ingredients.
Recipe Recommendations:
Utilizes the Food.com dataset stored on Snowflake.
Offers personalized recipe recommendations based on user preferences, dietary restrictions, and flavor profiles.
Technology Stack:
API Development: FastAPI
Natural Language Processing: OpenAI
Data Storage: Snowflake, Pinecone
User Interface: Streamlit
Automation: Apache Airflow
Deployment: Docker, AWS

Workflow:
Data acquisition from YouTube and Food.com.
Processing and summarization using OpenAI.
Recommendation generation based on user preferences.
User interaction through intuitive interfaces.
Automation of data processing tasks.
Deployment on AWS for scalability.

Stakeholders:
The end users for FoodWizard include:
Cooking enthusiasts seeking recipe inspiration and guidance.
Individuals with dietary restrictions or specific flavor preferences looking for tailored recipe recommendations.
Those interested in leveraging technology to simplify their culinary journey and explore new dishes.

CodeLab: https://codelabs-preview.appspot.com/?file_id=1T4FIak6iigOSCrGLP44bsKpyt_S_kZ1uKInPsoNiBUM#0

Architecture Diagram:
<img width="908" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/6dfb6c52-9854-4d84-9e39-8517705e1918">


Methodlogy: 


Data Acquisition:
Fetch cooking tutorial links from YouTube or Blog, sent by user through chrome extension
Scrape recipe data from sources - AllRecipes.com and BBC Food

Chrome Extension:
Develop a Chrome extension to allow users to send cooking tutorial videos from YouTube or specific blogs to be documented, attached to his account


<img width="609" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/e7bb1bfd-63c5-4514-b2c4-6c9538990d4c">

Data Processing and Summarization:
Process and summarize recipe data using OpenAI's natural language processing capabilities

<img width="1245" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/c52eee50-ac02-47d9-a253-9b857a03b0a3">

Recommendation Generation:
Generate personalized recipe recommendations based on user preferences and dietary restrictions
Store recipes from DB as embeddings in Pinecone for efficient retrieval

<img width="884" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/c5873c80-6106-4881-aaf6-119de95fbbf1">


User Interaction:
Develop a Streamlit interface for users to specify preferences, fetch all recipes documented for the user, and explore summarized recipes and recommendations
Implement filters and search functionality to search for videos and display top-matched recipes from Pinecone

Web Scraping:
Create a web scraper to crawl and extract recipe data from AllRecipes.com and BBC Food websites periodically
Update the Snowflake database with the latest scraped recipe data

Scheduling and Automation:
Implement a scheduler to periodically scrape recipe data from websites
Utilize Apache Airflow to automate data processing tasks, including video processing, summarization, embedding generation, and web scraping

Deployment:
Containerize the application using Docker for consistency and portability
Deploy the containerized application on Amazon Web Services (AWS) for scalability and reliability

Testing:
Implement both Unit testing to validate the functionality and integration of different components within the application.
Implement Continuous Integration (CI) pipeline using Git Actions to automate testing and build upon code changes.


Resources and Team:

1. Tools and Technologies:
   - Python (v3.9.7): A versatile programming language used for developing various components of the application.
   - FastAPI (v0.68.1): A modern, fast (high-performance), web framework for building APIs with Python 3.7+.
   - OpenAI: A leading artificial intelligence research laboratory, providing tools and APIs for natural language processing tasks.
   - Snowflake: A cloud-based data warehousing platform designed to handle large-scale data analytics.
   - Docker (v20.10.9): A platform for developing, shipping, and running applications in containers.
   - AWS (Amazon Web Services): A comprehensive cloud computing platform offering various services for computing, storage, database, and more.
   - Streamlit (v1.1.0): An open-source Python library that makes it easy to create interactive web apps for data analysis and machine learning models.
   - Apache Airflow (v2.1.4): A platform to programmatically author, schedule, and monitor workflows.
   - Pydantic (v1.8.3): A data validation library in Python for defining data schemas and ensuring data integrity.
  - Pinecone: A scalable vector database designed for real-time similarity search and recommendation systems, offering high-performance retrieval of embeddings for efficient similarity computations.
[https://www.pinecone.io/](https://www.pinecone.io/)


2. External Libraries and Dependencies:
   - OpenAI's Python client library (openai-python v0.18.0): Used for interacting with OpenAI's APIs for natural language processing tasks.

3. Data Sources:
   - YouTube: A video-sharing platform where users can find cooking tutorial videos.
   - Food.com: A comprehensive database of recipes and cooking-related content.
     https://www.kaggle.com/datasets/kanishk307/6000-indian-food-recipes-dataset     

4. Documentation and References:
   - FastAPI Documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
   - OpenAI API Documentation: [https://beta.openai.com/docs/](https://beta.openai.com/docs/)
   - Snowflake Documentation: [https://docs.snowflake.com/en/user-guide-intro.html](https://docs.snowflake.com/en/user-guide-intro.html)
   - Docker Documentation: [https://docs.docker.com/](https://docs.docker.com/)
   - AWS Documentation: [https://aws.amazon.com/documentation/](https://aws.amazon.com/documentation/)
   - Streamlit Documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)
   - Apache Airflow Documentation: [https://airflow.apache.org/docs/apache-airflow/stable/index.html](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
   - Pydantic Documentation: [https://pydantic-docs.helpmanual.io/](https://pydantic-docs.helpmanual.io/)
   - Pinecone Documentation: [https://www.pinecone.io/](https://www.pinecone.io/)

These resources provide comprehensive documentation, tutorials, and references for the tools, technologies, and libraries used in the project, aiding in the development and understanding of FoodWizard.

Team:
  - Hariharan Sundaram
  - Asawari Kadam
  - Rutuja Kute

