import snowflake.connector
import pinecone
from pinecone import Pinecone, PodSpec, ServerlessSpec
from langchain.embeddings.openai import OpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv
import os
import openai
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
# from uuid import uuid4
# from tqdm.auto import tqdm
import pandas as pd
import string
import random
# from PyPDF2 import PdfReader

# import boto3
# from botocore.exceptions import NoCredentialsError
import os
from urllib.parse import urlparse
from pathlib import Path

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.engine import URL
load_dotenv()
print(os.getenv('SNOWFLAKE_USER'))
print(os.getenv('SNOWFLAKE_PASSWORD'))
print(os.getenv('SNOWFLAKE_ACCOUNT'))

def fetch_snowflake_data():
    # Connect to Snowflake
    base_url = URL.create(
    "snowflake",
    username=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    host=os.getenv('SNOWFLAKE_ACCOUNT'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
)   
    engine = create_engine(base_url)
    connection = engine.connect()

        # Query learning outcome statements
    query = f"SELECT * FROM web_scraped_data"
  
    result=connection.execute(query)
    los_data = result.fetchall()
    connection.close()
    return los_data


# data=fetch_snowflake_data()
# for d in data:
#     print(d)
#     break


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
index_name = 'fooddata'

api_key = os.getenv("PINECONE_API_KEY")
print(api_key)

# initialize connection to pinecone
pinecone_client = Pinecone(api_key=api_key)

 


def deleteAndCreatePineconeIndex():
    # check if index already exists (it shouldn't if this is first time)
    if len(pinecone_client.list_indexes()) > 0:
        pinecone_client.delete_index(name=pinecone_client.list_indexes()[0].name)
    
    # Create index
    pinecone_client.create_index(
        index_name,
        dimension=1536,
        metric='dotproduct',
    spec=ServerlessSpec(
    cloud="aws",
    region="us-east-1"
  )
    
    )
    print("Deleted prev pinecone index and created new one")


index = pinecone_client.Index(index_name)   
# RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet


def create_embeddings_and_upsert(fooddata):
    embed_model = "text-embedding-3-small"
    food_embedding_to_upsert =[]
    # RecipeName_embedding_to_upsert = []
   
    df = pd.DataFrame(fooddata)
    for i, row in df.iterrows():
    
        input = f"""The recipe name is "{row.recipename}". 
        It has a preparation time of {row.preptimeinminutes} minutes, a cook time of "{row.cooktimeinminutes}" minutes, and a total time of "{row.totaltimeinminutes}" minutes. This recipe serves "{row.servings}" people and belongs to 
        the "{row.cuisine}" cuisine category. This recipe falls under the "{row.course}" course category and is suitable for a "{row.diet}" diet.  The ingredients include "{row.ingredients}"
        The instructions involve "{row.instructions}". Additionally, a YouTube link to a video demonstrating the recipe is provided:{row.youtubelink}"""
    
  
        food_embeddings= openai_client.embeddings.create(
        input=input if input else "Not mentioned" , model=embed_model
    )
        print(f"uploaded embedding {i}")
   
        
        food_embedding_to_upsert.append({'id': row.id , 'values': food_embeddings.data[0].embedding, 'metadata': {'RecipeName': row.recipename,'TotalTimeInMinutes': row.totaltimeinminutes,'Servings': row.servings,'Cuisine': row.cuisine,'Diet': row.diet, 'Course': row.course,'YoutubeLink': row.youtubelink}})
       
# RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet

    print("sucessfully created all embeddings")  
    def chunk_list(lst, batch_size):
        """Chunk a list into batches of specified size."""
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]

    # Example list
     # Sample list with 1000 elements

    # Chunking into batches of 100
    batched_list = list(chunk_list(food_embedding_to_upsert, 100))

    # Accessing all chunks
    count = 0
    for chunk in batched_list:
        count += 1
        index.upsert(index_name=index_name, vectors=chunk, namespace=("Recipe"))
        print(f"Chunk upserted {count}")

    
  
    print("successfully upserte all")




fooddata=fetch_snowflake_data()
deleteAndCreatePineconeIndex()
create_embeddings_and_upsert(fooddata)