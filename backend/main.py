import fastapi
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request, Depends
from pydantic import BaseModel, AnyHttpUrl
from queryvectordb import getrecommendedrecipes
import os
import pandas as pd
import uvicorn
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import snowflake.connector
from dotenv import load_dotenv
import sys

sys.path.insert(0, '/Users/asawari/Desktop/aaaaaa/FoodWizardApp/frontend')

from database import connect_to_snowflake, get_favorite_recipes

load_dotenv()
app = FastAPI()

# base url 

BASE_URL = os.getenv("BASE_URL")

# Replace with your Snowflake connection details
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

# Connect to Snowflake function
def connect_to_snowflake():
    ctx = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        schema=SNOWFLAKE_SCHEMA,
    )
    return ctx

USER_FAVORITE_URL = 'USER_FAVORITE_URL'
USER_INFO = 'USER_INFO'

create_database_query = f"CREATE DATABASE IF NOT EXISTS {SNOWFLAKE_DATABASE};"

# Creating warehouse for the cfa databases
create_warehouse_query = f"""CREATE WAREHOUSE IF NOT EXISTS {SNOWFLAKE_WAREHOUSE} WITH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 180
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE; 
"""


create_user_fav_url_table_query = f"""
CREATE TABLE IF NOT EXISTS {USER_FAVORITE_URL} (
    USER_URL_ID NUMBER AUTOINCREMENT,
    UserID NUMBER,
    Email VARCHAR(255),
    URL VARCHAR(255) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES USER_INFO(ID),
    PRIMARY KEY (USER_URL_ID)
);
"""

create_user_info_table_query = f"""
CREATE TABLE IF NOT EXISTS {USER_INFO} (
    ID NUMBER AUTOINCREMENT,
    Email VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    PRIMARY KEY (ID),
    UNIQUE(Email)
);
"""

ctx = connect_to_snowflake()
cursor = ctx.cursor()
cursor.execute(create_database_query)
cursor.execute(create_warehouse_query)

class DataItem(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to Foodwizard server"}



@app.get(f"/snowflake_query")
async def query_snowflake():
    
    try:
        # Establish connection
        ctx = connect_to_snowflake()
        cursor = ctx.cursor()

        # Sample query (replace with your actual query logic)
        query = f"SELECT RecipeName, PrepTimeInMinutes, CookTimeInMinutes, TotalTimeInMinutes, Servings, Cuisine, Ingredients, Instructions, Tags, YouTubeLink, Course, Diet FROM  web_scraped_data"

        cursor.execute(query)
        data = cursor.fetchall()
       
        column_names = [desc[0] for desc in cursor.description]
        # Close connection
        cursor.close()
        ctx.close()

        # Create a DataFrame with the fetched data and column names
       
        return {"data": data, "column_names":column_names}


    except Exception as e:
        return {"error": str(e)}
    

@app.get("/get_recommeded_recipies")
async def get_recommeded_recipies(request:dict):
    text=request.get("text")
    try:
       listofdata=getrecommendedrecipes(text)
       return {"listofdata":listofdata}


    except Exception as e:
        return {"error": str(e)}
    
@app.post("/process_url")
async def receive_data(data_item: DataItem, authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # Process the received data
    token = authorization.credentials
    print("Received URL:", data_item.url)
    #print("Received User ID:", data_item.email)
    try:
        decoded_data = jwt.decode(jwt=token,
                                algorithms=["RS256"],
                                options={"verify_signature": False
                                })

                # Add the email and name to the decoded_data dictionary
        email = decoded_data.get("email")  # Assuming the email is present in the decoded token
        name = decoded_data.get("name")  
        

        # Here, you can write the email, name, and other data to your database or perform any other operations
        validate_user_and_insert( email, name, data_item.url)
        return {"message": "Data received successfully"}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/favorite-recipes/{user_email}")
def get_favorite_recipes_api(user_email: str):
    ctx = connect_to_snowflake()
    cursor = ctx.cursor()
    cursor.execute("SELECT DISTINCT title, link_video, generated_recipe, user_email FROM video_table WHERE user_email = %s", (user_email,))
    favorite_recipes = cursor.fetchall()  # Fetch all rows
    print('favorite_recipes:', favorite_recipes)
    result = []
    for recipe in favorite_recipes:
        TITLE , LINK_VIDEO , GENERATED_RECIPE , USER_EMAIL = recipe
        result.append({"TITLE": TITLE, "LINK_VIDEO": LINK_VIDEO, "GENERATED_RECIPE": GENERATED_RECIPE, "USER_EMAIL": USER_EMAIL})
    ctx.close()
    return result
    
def insert_user_info(cursor, email, name):
    try:
        # Check if the user exists in USER_INFO
        check_user_query = "SELECT ID FROM USER_INFO WHERE Email = %s"
        cursor.execute(check_user_query, (email,))
        result = cursor.fetchone()

        if result:
            # User already exists
            print('User already exists')
            return result[0]  # Return the existing user ID
        else:
            # User doesn't exist, insert into USER_INFO
            insert_user_query = "INSERT INTO USER_INFO (Email, Name) VALUES (%s, %s)"
            cursor.execute(insert_user_query, (email, name))

            # Get the newly inserted user ID
            cursor.execute(check_user_query, (email,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the newly inserted user ID
            else:
                print(f"Error: Failed to retrieve user ID for email: {email}")
                return None
    except Exception as e:
        print(f"Error inserting user info: {e}")
        return None

def insert_favorite_url(cursor, email, user_id, url):
    try:
        # Insert URL into USER_FAVORITE_URL
        insert_url_query = "INSERT INTO USER_FAVORITE_URL (UserID,email, URL) VALUES (%s, %s, %s)"
        cursor.execute(insert_url_query, (user_id, email, url))
        print(f"URL added for user ID {user_id}, email {email}: url={url}")
        return True
    except Exception as e:
        print(f"Error inserting favorite URL: {e}")
        return False

def validate_user_and_insert(email, name, url):
    try:
        # Establish connection
        cursor = ctx.cursor()
        cursor.execute(create_user_info_table_query)
        cursor.execute(create_user_fav_url_table_query)

        # Insert user info
        user_id = insert_user_info(cursor, email, name)
        if user_id is not None:
            # User info inserted successfully, insert favorite URL
            insert_favorite_url(cursor, email, user_id, url)

        cursor.close()
        ctx.commit()
    except Exception as e:
        print(f"Error: {e}")
        if ctx:
            ctx.rollback()

# Define your Chrome extension's origin
chrome_extension_origin = "chrome-extension://jbimcanopnhpajhgmnippneolodejkeg"

# Enable CORS middleware with specific origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[chrome_extension_origin],
    allow_methods=["POST"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, root_path="/api/v1", log_level="debug")