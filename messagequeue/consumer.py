from kafka import KafkaConsumer
from json import loads
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
import ffmpeg
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from pytube import YouTube

load_dotenv(verbose=True, override=True)

TABLE_NAME_VIDEO = os.getenv('SNOWFLAKE_TABLE_VIDEO')
DATABASE_NAME = os.getenv('SNOWFLAKE_DATABASE')
WAREHOUSE_NAME = os.getenv('SNOWFLAKE_WAREHOUSE')
LOCAL_FILE_PATH='/tmp/audio_files'
ORIG_AUDIO_FILE_NAME='original_audio.mp3'
files_to_delete = []

# Snowflake base URL
base_url = URL.create(
    "snowflake",
    username=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    host=os.getenv('SNOWFLAKE_ACCOUNT'),
)

# Snowflake Engine
engine = create_engine(base_url)

# OpenAI Client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def downloadAudioToSystem(link):
    global files_to_delete
    print('Starting video stream download')
    ytStream = YouTube(link)
    audio_stream = ytStream.streams.filter(only_audio=True, mime_type='audio/mp4').desc().first()
    audio_file = audio_stream.download(output_path=LOCAL_FILE_PATH) 
    temp_file_path = os.path.join(LOCAL_FILE_PATH, 'temp_original_audio'+os.path.splitext(audio_file)[1])
    os.rename(audio_file, temp_file_path) 
    ffmpeg.input(temp_file_path).output(os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)).run(overwrite_output=True)
    # To delete at a later stage
    files_to_delete = [temp_file_path, os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)]
    print(ytStream.title + " has been successfully downloaded.")
    return ytStream.title

def audioFileSize():
    path = os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)
    return os.path.getsize(path) / (1024*1024)
    
def convertToTranscript():
    print('Starting audio to text transcription')
    path = os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)
    audio_data_buffer = open(path, "rb")
    translation = openai_client.audio.translations.create(
        model="whisper-1", 
        file=audio_data_buffer
    )
    print('Audio to text transcription successful')
    return translation.text

def convertToRecipeFormat(context):
    prompt = f"""
    Ingredients:
    Detailed Cooking Instructions: 
    Tags: 

    Convert into the standard recipe format given above from the context given below. Do not include a title. If you are not sure(probability < 50%), then fill the field with None. If the context does not correspond to a recipe then return "This link does not talk about cooking. Too bad!"
    {context}
    """
    stream = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=8000,
    stream=True,
    )
    text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            text = text + chunk.choices[0].delta.content
    return text

def uploadToSnowflake(title, recipe, link, system_message):
    print("Starting snowflake upload")
    values_str = "('{title}', '{generated_recipe}', '{link_video}', '{system_message}')".format(
            title=(title if title else 'NULL'), generated_recipe=(recipe if recipe else 'NULL'), link_video=link, system_message=(system_message if system_message else 'NULL')
        )
    try:
        connection = engine.connect()
        connection.execute(f'USE DATABASE {DATABASE_NAME};')
        connection.execute("BEGIN")
        connection.execute(f"""INSERT INTO {TABLE_NAME_VIDEO}
                            VALUES
                            {values_str};""")
        connection.execute("COMMIT")
        print('Snowflake upload successful')
    except Exception as e:
        print(e)
        exit(1)
    finally:
        connection.close()
        engine.dispose()

def deleteLocalAudioFiles():
    print('Starting local audio files deletion')
    global files_to_delete
    for path in files_to_delete:
        try:
            os.remove(path)
        except OSError:
            pass
    files_to_delete = []
    print('Delete local audio files successful')

def handleURL(link):
    video_title = downloadAudioToSystem(link=link)
    if(audioFileSize() >= 25):
        # Add a message into snowflake with link
        print('File too large')
        uploadToSnowflake(link=link, system_message='The video is too long. System can support only videos under 23mins')
        return
    transcribed_text = convertToTranscript()
    recipe_generated = convertToRecipeFormat(context=transcribed_text)
    uploadToSnowflake(title=video_title, recipe=recipe_generated, link=link, system_message='Successful run')
    deleteLocalAudioFiles()

def snowflakeDDLQueries():
    # Creating database for storing food wizard data
    create_foodwiz_database_query = f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};"

    # Creating warehouse for the food wizard databases
    create_foodwiz_warehouse_query = f"""CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE_NAME} WITH
        WAREHOUSE_SIZE = 'X-SMALL'
        AUTO_SUSPEND = 180
        AUTO_RESUME = TRUE
        INITIALLY_SUSPENDED = TRUE; 
    """

    # Creating warehouse for the food wizard table
    create_video_table_query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME_VIDEO} (
        title STRING,
        generated_recipe String,
        link_video STRING,
        system_message STRING,
        PRIMARY KEY (link_video)
    )
    """
    try:
        connection = engine.connect()
        connection.execute(create_foodwiz_warehouse_query)
        connection.execute(create_foodwiz_database_query)
        connection.execute(f'USE WAREHOUSE {WAREHOUSE_NAME};')
        connection.execute(f'USE DATABASE {DATABASE_NAME};')
        connection.execute(create_video_table_query)
        print('Tables created successfully')
    except Exception as e:
        print(e)
        exit(1)
    finally:
        connection.close()
        engine.dispose()


def startConsumer():
        snowflakeDDLQueries()
        consumer = KafkaConsumer(
            'url_queue',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='food-wizard-group'
        )

        for message in consumer:
            try:
                link = message.value.decode("utf-8")
                print(link)
                handleURL(link=link)
            except Exception as e:
                print(f"URL Message Consumer: {e}")
                time.sleep(2)
                # Add a message into snowflake with link
                uploadToSnowflake(link=link, system_message='Failed due to unknown reason. Please try again later!')
                deleteLocalAudioFiles()

def main():
    startConsumer()

if __name__ == "__main__":
    main()
    