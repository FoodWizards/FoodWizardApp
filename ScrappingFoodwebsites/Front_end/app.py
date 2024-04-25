import streamlit as st

def main():
    st.title("Recipe Input App")

    # Input fields
    recipe_name = st.text_input("Recipe Name")
    prep_time = st.number_input("Prep Time (minutes)", min_value=0, step=1)
    cook_time = st.number_input("Cook Time (minutes)", min_value=0, step=1)
    total_time = st.number_input("Total Time (minutes)", min_value=0, step=1)
    servings = st.number_input("Servings", min_value=1, step=1)
    cuisine = st.text_input("Cuisine")
    ingredients = st.text_area("Ingredients")
    instructions = st.text_area("Instructions")
    tags = st.text_input("Tags (comma separated)")
    youtube_link = st.text_input("YouTube Link")
    course = st.selectbox("Course", ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Appetizer", "Side Dish", "Drink"])
    diet = st.selectbox("Diet", ["Vegetarian", "Vegan", "Gluten Free", "Keto", "Paleo", "Low Carb", "Low Fat", "Low Calorie"])

    # Submit button
    if st.button("Submit"):
        # Display the entered data
        st.write("## Recipe Details")
        st.write(f"**Recipe Name:** {recipe_name}")
        st.write(f"**Prep Time:** {prep_time} minutes")
        st.write(f"**Cook Time:** {cook_time} minutes")
        st.write(f"**Total Time:** {total_time} minutes")
        st.write(f"**Servings:** {servings}")
        st.write(f"**Cuisine:** {cuisine}")
        st.write("**Ingredients:**")
        st.write(ingredients)
        st.write("**Instructions:**")
        st.write(instructions)
        st.write(f"**Tags:** {tags}")
        st.write(f"**YouTube Link:** {youtube_link}")
        st.write(f"**Course:** {course}")
        st.write(f"**Diet:** {diet}")

if __name__ == "__main__":
    main()
