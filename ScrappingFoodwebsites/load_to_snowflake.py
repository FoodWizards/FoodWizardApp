from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.engine import URL
import pandas as pd
import numpy as np

load_dotenv()

TABLE_NAME = os.getenv('SNOWFLAKE_TABLE')


DATABASE_NAME = os.getenv('SNOWFLAKE_DATABASE')
WAREHOUSE_NAME = os.getenv('SNOWFLAKE_WAREHOUSE')


base_url = URL.create(
    "snowflake",
    username=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    host=os.getenv('SNOWFLAKE_ACCOUNT'),
)

# Creating database for storing cfa data
create_database_query = f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};"

# Creating warehouse for the cfa databases
create_warehouse_query = f"""CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE_NAME} WITH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 180
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE; 
"""
# RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet

def create_scraped_data_table(connection):
    # Creating table for scraped data
    create_scraped_data_table_query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    ID STRING,
    RecipeName TEXT,
    PrepTimeInMinutes INTEGER,
    CookTimeInMinutes INTEGER,
    TotalTimeInMinutes INTEGER,
    Servings INTEGER,
    Cuisine TEXT,
    Ingredients TEXT,
    Instructions TEXT,
    Tags TEXT,
    YouTubeLink TEXT,
    Course TEXT,
    Diet TEXT,
    PRIMARY KEY (RecipeName)
)
"""
    connection.execute(create_scraped_data_table_query)




def execute_ddl_queries(connection):
    connection.execute(create_warehouse_query)
    connection.execute(create_database_query)
    connection.execute(f'USE WAREHOUSE {WAREHOUSE_NAME};')
    connection.execute(f'USE DATABASE {DATABASE_NAME};')
    create_scraped_data_table(connection=connection)
   
# RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet

def upload_into_web_scraped_table(connection):
    data_file_name = 'clean_data.csv'
    connection.execute(f"PUT file://clean_csv/clean_data.csv @{DATABASE_NAME}.PUBLIC.%{TABLE_NAME};")
    print("Uploaded file -----------------")
    copy_into_webscraped_db = f"""COPY INTO {DATABASE_NAME}.PUBLIC.{TABLE_NAME}
        FROM '@{DATABASE_NAME}.PUBLIC.%{TABLE_NAME}'
        FILES = ('{data_file_name}.gz')
        FILE_FORMAT = (
            TYPE=CSV,
            SKIP_HEADER=1,
            FIELD_DELIMITER=',',
            TRIM_SPACE=FALSE,
            FIELD_OPTIONALLY_ENCLOSED_BY='"',
            REPLACE_INVALID_CHARACTERS=TRUE,
            DATE_FORMAT=AUTO,
            TIME_FORMAT=AUTO,
            TIMESTAMP_FORMAT=AUTO
        )
        ON_ERROR=ABORT_STATEMENT
        PURGE=TRUE
    """
  
    connection.execute(copy_into_webscraped_db)





# def create_role_permission(connection):
#     role_name = 'fooddata_dev_role'
#     connection.execute(f'CREATE OR REPLACE ROLE {role_name};')
#     connection.execute(f'GRANT ROLE {role_name} TO ROLE SYSADMIN;')
    
#     # Grant permission to roles
#     connection.execute(f'GRANT ALL ON WAREHOUSE {WAREHOUSE_NAME} TO ROLE {role_name};')
#     connection.execute(f'GRANT ALL ON DATABASE {DATABASE_NAME} TO ROLE {role_name};')
#     connection.execute(f'GRANT ALL ON ALL SCHEMAS IN DATABASE {DATABASE_NAME} TO ROLE {role_name};')


engine = create_engine(base_url)

try:
    connection = engine.connect()
    execute_ddl_queries(connection=connection)
    print('Completed databases, warehouse and table creation')
    # create_role_permission(connection=connection)
    # print('Completed role creation and granted permissions successfully')
    upload_into_web_scraped_table(connection=connection)
    print('Data upload into web scraped table successful')
  

except Exception as e:
    print(e)
finally:
    connection.close()
    engine.dispose()