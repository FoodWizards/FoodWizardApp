# database.py
import snowflake.connector
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def connect_to_snowflake():
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
    SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
    SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
    SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
    SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

    ctx = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        schema=SNOWFLAKE_SCHEMA,
    )
    return ctx

def create_user_info_table(ctx):
    USER_INFO = 'User_info'
    create_user_info_table_query = f"""
    CREATE TABLE IF NOT EXISTS {USER_INFO} (
        ID NUMBER AUTOINCREMENT,
        Email VARCHAR(255) NOT NULL,
        Name VARCHAR(255) NOT NULL,
        PRIMARY KEY (ID),
        UNIQUE(Email)
    );
    """
    cursor = ctx.cursor()
    cursor.execute(create_user_info_table_query)
    ctx.commit()

def insert_user_info(ctx, email, name):
    cursor = ctx.cursor()
    check_query = "SELECT COUNT(*) FROM User_info WHERE Email = %s"
    cursor.execute(check_query, (email,))
    existing_user_count = cursor.fetchone()[0]  # Get the first element (count)

    if existing_user_count == 0:
        # Insert user information if not already present
        insert_query = "INSERT INTO User_info (Email, name) VALUES (%s, %s)"
        cursor.execute(insert_query, (email, name))
        ctx.commit()
        return True
    else:
        return False

def get_favorite_recipes(ctx, email):
    cursor = ctx.cursor()
    search_recipe_query = "SELECT link_video, generated_recipe, user_email FROM video_table WHERE user_email = %s"
    cursor.execute(search_recipe_query, (email,))
    fav_recipe = cursor.fetchall()
