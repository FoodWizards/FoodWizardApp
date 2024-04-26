import streamlit as st
import requests
import pandas as pd
import os
import openai
from openai import OpenAI

BASE_URL = os.getenv("BASE_URL")
Data_URL = f"http://{BASE_URL}/get_recommeded_recipies"

def _fetchAnswerFromGPT(contextStr):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""Dont infer just format this given context below '{contextStr} and do not include text like these 'Here is the formatted version of the given context:' """
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": """You are a helpful bot who just formats the text given by the user. """},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def find_recipe():
    st.title("Find Your Recipe")
    if 'input_text' not in st.session_state:
        st.session_state['input_text'] = ''

    # Get the input text from session_state
    text = st.session_state['input_text']

    text = st.text_area("Instructions", height=200, help="Enter the cooking instructions")
    clear_button = st.button("Clear Input")

    # If the "Clear Input" button is clicked, clear the input text
    if clear_button:
        st.session_state['text'] = ''
        st.experimental_rerun()

    st.session_state['input_text'] = text

    data = {"text": text}
    response = requests.get(Data_URL, json=data)

    # Check if request was successful
    if response.status_code == 200:
        # Display the response (assuming JSON format)
        data = response.json()
        listofdata = data["listofdata"]

        if st.button("Submit"):
            # Process the input data
            # Display the input data
            st.write("### Recipe Data:")
            recipe_data = pd.DataFrame(listofdata)

            # Create an expander for each recipe
            for index, row in recipe_data.iterrows():
                recipe_name = row['RecipeName']
                recipe_details = {
                    'TotalTimeInMinutes': row['TotalTimeInMinutes'] if row['TotalTimeInMinutes'] else 'Not Mentioned',
                    'Servings': row['Servings'] if row['Servings'] else 'Not Mentioned',
                    'Cuisine': row['Cuisine'] if row['Cuisine'] else 'Not Mentioned',
                    'Diet': row['Diet'] if row['Diet'] else 'Not Mentioned',
                    'Course': row['Course'] if row['Course'] else 'Not Mentioned',
                    'YoutubeLink': row['YoutubeLink'] if row['YoutubeLink'] else 'Not Mentioned',
                    'CookTimeInMinutes': row['CookTimeInMinutes'] if row['CookTimeInMinutes'] else 'Not Mentioned',
                    'PrepTimeInMinutes': row['PrepTimeInMinutes'] if row['PrepTimeInMinutes'] else 'Not Mentioned',
                    'Instructions': _fetchAnswerFromGPT(row['Instructions']) if row['Instructions'] else 'Not Mentioned',
                    'Ingredients': _fetchAnswerFromGPT(row['Ingredients']) if row['Ingredients'] else 'Not Mentioned'
                }
        
                with st.expander(recipe_name):
                    st.write('**Recipe Details:**')
                    for key, value in recipe_details.items():
                        st.write(f'**{key}:** {value}')




