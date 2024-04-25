import streamlit as st
import pandas as pd
import requests
# "http://host.docker.internal:8080/snowflake_query"
API_URL = "http://localhost:8000/snowflake_query"
Data_URL = "http://localhost:8000/get_recommeded_recipies"


# Sample recipe data (replace this with your actual data)
# recipe_data = pd.read_csv("/Users/rutujakute/Documents/ScrappingFoodwebsites/clean_csv/clean_data.csv")

response = requests.get(API_URL)
    # Check if request was successful
if response.status_code == 200:
        # Display the response (assuming JSON format)
        data= response.json()
        column_names = data["column_names"]
        data = data["data"]
        recipe_data= pd.DataFrame(data, columns=column_names)



def filter_recipes(data, filters):
    filtered_data = data
    filtered_data = filtered_data.fillna("")
    for key, value in filters.items():
        if value:
            # Check if the column is of string type
            if filtered_data[key].dtype == 'O':
                filtered_data = filtered_data[filtered_data[key].str.contains(str(value), case=False)]
            # Check if the column is of integer type
            elif filtered_data[key].dtype == 'int64' or filtered_data[key].dtype == 'float64':
                filtered_data = filtered_data[filtered_data[key] == value]
    return filtered_data

def main():
    st.title("Recipe List")
    default_value = " "
    # Filter options
   
    filters = {}
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        filters = {}
        filters["RECIPENAME"] = st.text_input("Recipe Name")
        filters["SERVINGS"] = st.number_input("Servings", min_value=0, step=1)

    with col2:
        filters["CUISINE"] = st.selectbox("Cuisine", recipe_data["CUISINE"].unique(), index=recipe_data["CUISINE"].unique().index(default_value) if default_value in recipe_data else None)
        filters["COURSE"] = st.selectbox("Course",recipe_data["COURSE"].unique(),index=recipe_data["COURSE"].unique().index(default_value) if default_value in recipe_data else None)

    with col3:
        filters["DIET"] = st.selectbox("Diet", recipe_data["DIET"].unique(),index=recipe_data["DIET"].unique().index(default_value) if default_value in recipe_data else None)
        filters["TOTALTIMEINMINUTES"] = st.number_input("Total Time (minutes)", min_value=0, step=1)

    # Additional inputs below the columns
   
    filters["INGREDIENTS"] = st.text_input("Ingredients")

    # Apply filters
    if st.button("Apply Filters"):
        filtered_recipes = filter_recipes(recipe_data, filters)

        # Display filtered recipes
        st.subheader("Filtered Recipes")
        if len(filtered_recipes) == 0:
            st.write("No recipes found with the given filters.")
        else:
            st.write(filtered_recipes, style={"overflowY": "scroll", "height": "600px"})
    else: 
        st.write(recipe_data, style={"overflowY": "scroll", "height": "600px"})

if __name__ == "__main__":
    main()

