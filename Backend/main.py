from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import snowflake.connector
from dotenv import load_dotenv
from ..frontend.database import connect_to_snowflake, get_favorite_recipes


load_dotenv()


app = FastAPI()

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
    Email VARCHAR(255) NOT NULL,
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
cursor.execute(create_user_info_table_query)
cursor.execute(create_user_fav_url_table_query)
ctx.commit()

class DataItem(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to FoodWizard"}

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

@app.get("/favorite-recipes/{email}")
def get_favorite_recipes_api(email: str):
    ctx = connect_to_snowflake()
    cursor = ctx.cursor()
    cursor.execute("SELECT DISTINCT TITLE, LINK_VIDEO, GENERATED_RECIPE FROM VIDEO_TABLE WHERE email = %s", (email,))
    favorite_recipes = cursor.fetchall()  # Fetch all rows
    result = []
    for recipe in favorite_recipes:
        TITLE, LINK_VIDEO, GENERATED_RECIPE = recipe
        result.append({"TITLE": TITLE, "LINK_VIDEO": LINK_VIDEO, "GENERATED_RECIPE": GENERATED_RECIPE})
    ctx.close()
    return result
    
def validate_user_and_insert(email, name, url):
    try:
        # Establish connection
        cursor = ctx.cursor()

        # Check if the user exists in USER_INFO
        check_user_query = "SELECT ID FROM USER_INFO WHERE Email = %s"
        cursor.execute(check_user_query, (email,))
        result = cursor.fetchone()

        if result:
            # User exists, add email and url to USER_FAVORITE_URL
            user_id = result[0]
            insert_url_query = "INSERT INTO USER_FAVORITE_URL (UserID, Email, URL) VALUES (%s, %s, %s)"
            cursor.execute(insert_url_query, (user_id, email, url))
            print(f"URL added for existing user: email={email}, url={url}")
        else:
            # User doesn't exist, add to USER_INFO and USER_FAVORITE_URL
            insert_user_query = "INSERT INTO USER_INFO (Email, Name) VALUES (%s, %s)"
            cursor.execute(insert_user_query, (email, name))

            # Get the newly inserted user ID
            get_user_id_query = "SELECT ID FROM USER_INFO WHERE Email = %s"
            cursor.execute(get_user_id_query, (email,))
            user_id = cursor.fetchone()

            insert_url_query = "INSERT INTO USER_FAVORITE_URL (UserID, URL) VALUES (%s, %s)"
            cursor.execute(insert_url_query, (user_id, url))
            print(f"New user added: email={email}, name={name}, url={url}")

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

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
