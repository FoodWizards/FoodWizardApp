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

Architecture Diagram:<img width="980" alt="image" src="https://github.com/FoodWizards/FoodWizardApp/assets/114360071/19dc0dc8-1f1b-411a-8624-0d05287f4d5c">

Data Link:
Food.com data from Kaggle can be found below
https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
