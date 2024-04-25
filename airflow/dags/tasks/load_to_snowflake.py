from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.engine import URL
import constants

load_dotenv(verbose=True, override=True)

TABLE_NAME = os.getenv('SNOWFLAKE_TABLE')
DATABASE_NAME = os.getenv('SNOWFLAKE_DATABASE')
WAREHOUSE_NAME = os.getenv('SNOWFLAKE_WAREHOUSE')

base_url = URL.create(
    "snowflake",
    username=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    host=os.getenv('SNOWFLAKE_ACCOUNT'),
)
engine = create_engine(base_url)

def _create_scraped_data_table(connection):
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

def _execute_ddl_queries(connection):
    # Creating database for storing cfa data
    create_database_query = f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};"

    # Creating warehouse for the cfa databases
    create_warehouse_query = f"""CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE_NAME} WITH
        WAREHOUSE_SIZE = 'X-SMALL'
        AUTO_SUSPEND = 180
        AUTO_RESUME = TRUE
        INITIALLY_SUSPENDED = TRUE; 
    """
    connection.execute(create_warehouse_query)
    connection.execute(create_database_query)
    connection.execute(f'USE WAREHOUSE {WAREHOUSE_NAME};')
    connection.execute(f'USE DATABASE {DATABASE_NAME};')
    _create_scraped_data_table(connection=connection)

def _upload_into_web_scraped_table(filepath, connection):
    data_file_name = 'clean_data.csv'
    connection.execute(f"PUT file://{filepath} @{DATABASE_NAME}.PUBLIC.%{TABLE_NAME};")
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
    print("Uploadeded file into snowflake")

def start_upload(**kwargs):
    ti = kwargs['ti']
    cleaned_file_path = ti.xcom_pull(key=constants.XKEY_SCRAPED_CLEANED_FILE_PATH, task_ids=constants.TASK_CLEAN_VALIDATE_ID) 
    try:
        connection = engine.connect()
        _execute_ddl_queries(connection=connection)
        print('Completed databases, warehouse and table creation')
        _upload_into_web_scraped_table(filepath=cleaned_file_path, connection=connection)
        print('Data upload into web scraped table successful')
    
    except Exception as e:
        print(e)
    finally:
        connection.close()
        engine.dispose()