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
import json
import logging

logger = logging.getLogger(__name__)

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
    logger.info('Starting video stream download')
    ytStream = YouTube(link)
    audio_stream = ytStream.streams.filter(only_audio=True, mime_type='audio/mp4').desc().first()
    audio_file = audio_stream.download(output_path=LOCAL_FILE_PATH) 
    temp_file_path = os.path.join(LOCAL_FILE_PATH, 'temp_original_audio'+os.path.splitext(audio_file)[1])
    os.rename(audio_file, temp_file_path) 
    ffmpeg.input(temp_file_path).output(os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)).run(overwrite_output=True)
    # To delete at a later stage
    files_to_delete = [temp_file_path, os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)]
    logger.info(ytStream.title + " has been successfully downloaded.")
    return ytStream.title

def audioFileSize():
    path = os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)
    return os.path.getsize(path) / (1024*1024)
    
def convertToTranscript():
    logger.info('Starting audio to text transcription')
    path = os.path.join(LOCAL_FILE_PATH, ORIG_AUDIO_FILE_NAME)
    audio_data_buffer = open(path, "rb")
    translation = openai_client.audio.translations.create(
        model="whisper-1", 
        file=audio_data_buffer
    )
    logger.info('Audio to text transcription successful')
    return translation.text

def convertToRecipeFormat(context):
    print("Starting transcript to recipe conversion")
    prompt = f"""
    Ingredients:
    Detailed Cooking Instructions: 
    Tags: 

    Convert into the standard recipe format given above from the context given below. Do not include a title. If you are not sure(probability < 50%), then fill the field with None. If the context does not correspond to a recipe then return "This link does not talk about cooking or we were not able to understand it well. Sorry about that!"
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
    print("Transcript to recipe conversion successful")
    return text

def uploadToSnowflake(title, recipe, link, system_message, email):
    logger.info("Starting snowflake upload")
    values_str = "('{title}', '{generated_recipe}', '{link_video}', '{system_message}', '{user_email}')".format(
            title=(title if title else 'NULL'), generated_recipe=(recipe if recipe else 'NULL'), link_video=link, system_message=(system_message if system_message else 'NULL'), user_email=email
        )
    try:
        connection = engine.connect()
        connection.execute(f'USE DATABASE {DATABASE_NAME};')
        connection.execute("BEGIN")
        connection.execute(f"""INSERT INTO {TABLE_NAME_VIDEO}
                            VALUES
                            {values_str};""")
        connection.execute("COMMIT")
        logger.info('Snowflake upload successful')
    except Exception as e:
        logger.info(e)
        exit(1)
    finally:
        connection.close()
        engine.dispose()

def deleteLocalAudioFiles():
    logger.info('Starting local audio files deletion')
    global files_to_delete
    for path in files_to_delete:
        try:
            os.remove(path)
        except OSError:
            pass
    files_to_delete = []
    logger.info('Delete local audio files successful')

def handleURL(link, email):
    video_title = downloadAudioToSystem(link=link)
    if(audioFileSize() >= 25):
        # Add a message into snowflake with link
        logger.info('File too large')
        uploadToSnowflake(link=link, system_message='The video is too long. System can support only videos under 23mins', email=email)
        return
    transcribed_text = convertToTranscript()
    recipe_generated = convertToRecipeFormat(context=transcribed_text)
    uploadToSnowflake(title=video_title, recipe=recipe_generated, link=link, system_message='Successful run', email=email)
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
        user_email STRING,
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
        logger.info('Tables created successfully')
    except Exception as e:
        logger.info(e)
        exit(1)
    finally:
        connection.close()
        engine.dispose()

def forgiving_json_deserializer(blob):
    if blob is None:
        return None
    try:
        logger.info(blob.decode('utf-8'))
        logger.info('Done decoding')
        return json.loads(blob.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        logger.info('Unable to decode: %s', blob)
        return None
    except Exception as e:
        logger.info('Unable to decode: %s', blob)
        logger.info(e)
        return None


def startConsumer():
        consumer = KafkaConsumer(
            'url_queue',
            bootstrap_servers=['host.docker.internal:29092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='food-wizard-group',
            value_deserializer=forgiving_json_deserializer
        )

        for message in consumer:
            if message is None:
                continue
            try:
                link = message.value.get('url')
                email = message.value.get('email')
                if email is None or link is None:
                    continue
                logger.info(link)
                handleURL(link=link, email=email)
            except Exception as e:
                logger.info(f"URL Message Consumer: {e}")
                time.sleep(2)
                deleteLocalAudioFiles()

def main():
    logging.basicConfig(filename='/tmp/consumer.log', level=logging.INFO)
    snowflakeDDLQueries()
    count = 50
    while count > 0:
        count -= 1
        try:
            startConsumer()
        except Exception as e:
            logger.info(e)
            time.sleep(10)
    

if __name__ == "__main__":
    main()
    