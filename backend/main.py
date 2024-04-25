import fastapi
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from pydantic import BaseModel, AnyHttpUrl

from queryvectordb import getrecommendedrecipes
import os
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

import uvicorn


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




@app.get("/")
async def root():
    return {"message": "Hello, Welcome to Foodwizard server"}



@app.get("/snowflake_query")
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
    






if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")