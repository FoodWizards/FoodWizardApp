import streamlit as st
import requests
Data_URL = "http://localhost:8000/get_recommeded_recipies"
import pandas as pd

def main():
    st.title("Find Your Recipe")
    text = st.text_area("Instructions", height=200, help="Enter the cooking instructions")
    data = {"text": text}
    response = requests.get(Data_URL, json =data)
    # Check if request was successful
    if response.status_code == 200:
            # Display the response (assuming JSON format)
            data= response.json()
            listofdata = data["listofdata"]
        

    if st.button("Submit"):
        # Process the input data
       
        # Display the input data
        st.write("### Recipe Data:")
        recipe_data=pd.DataFrame(listofdata)
        st.write(recipe_data)

if __name__ == "__main__":
    main()
