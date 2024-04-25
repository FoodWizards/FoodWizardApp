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
    # PrepTimeInMinutes_embedding_to_upsert = []
    # CookTimeInMinutes_embedding_to_upsert	= []
    # TotalTimeInMinutes_embedding_to_upsert =[]
    # Servings_embedding_to_upsert= []
    # Cuisine_embedding_to_upsert= []
    # Ingredients_embedding_to_upsert	= []
    # Instructions_embedding_to_upsert= []
    # Tags_embedding_to_upsert= []
    # YouTubeLink_embedding_to_upsert	= []
    # Course_embedding_to_upsert= []
    # Diet_embedding_to_upsert= []
    df = pd.DataFrame(fooddata)
    for i, row in df.iterrows():
    # complete_data = str(data)
    #     food_embeddings  = openai_client.embeddings.create(
    #     input=complete_data, model=embed_model
    # )
        input = f"""The recipe name is "{row.recipename}". 
        It has a preparation time of {row.preptimeinminutes} minutes, a cook time of "{row.cooktimeinminutes}" minutes, and a total time of "{row.totaltimeinminutes}" minutes. This recipe serves "{row.servings}" people and belongs to 
        the "{row.cuisine}" cuisine category. This recipe falls under the "{row.course}" course category and is suitable for a "{row.diet}" diet.  The ingredients include "{row.ingredients}"
        The instructions involve "{row.instructions}". Additionally, a YouTube link to a video demonstrating the recipe is provided:{row.youtubelink}"""
    
    #     RecipeName_embeddings = openai_client.embeddings.create(
    #     input=row.recipename if row.recipename else "Not mentioned" , model=embed_model
      
    # )
        food_embeddings= openai_client.embeddings.create(
        input=input if input else "Not mentioned" , model=embed_model
    )
        print(f"uploaded embedding {i}")
    #     PrepTimeInMinutes_embeddings = openai_client.embeddings.create(
    #     input= str(row.preptimeinminutes) if row.preptimeinminutes else "Not mentioned" , model=embed_model
    # )
    #     CookTimeInMinutes_embeddings	= openai_client.embeddings.create(
    #     input= str(row.cooktimeinminutes) if row.cooktimeinminutes else "Not mentioned", model=embed_model
    # )
    #     TotalTimeInMinutes_embeddings= openai_client.embeddings.create(
    #     input=str(row.totaltimeinminutes) if row.totaltimeinminutes else "Not mentioned", model=embed_model
    # )
    #     Servings_embeddings= openai_client.embeddings.create(
    #     input=str(row.servings) if row.servings else "Not mentioned", model=embed_model
    # )
    #     Cuisine_embeddings= openai_client.embeddings.create(
    #     input=row.cuisine if row.cuisine else "Not mentioned", model=embed_model
    # )
    #     Ingredients_embeddings	= openai_client.embeddings.create(
    #     input=row.ingredients if row.ingredients else "Not mentioned", model=embed_model
    # )
    #     Instructions_embeddings= openai_client.embeddings.create(
    #     input=row.instructions if row.instructions else "Not mentioned"  , model=embed_model
    # )
    #     Tags_embeddings= openai_client.embeddings.create(
    #     input=row.tags if row.tags else "Not mentioned" , model=embed_model
    # )
    #     YouTubeLink_embeddings	= openai_client.embeddings.create(
    #     input=row.youtubelink if row.youtubelink else "Not mentioned", model=embed_model
    # )
    #     Course_embeddings= openai_client.embeddings.create(
    #     input=row.course if row.course else "Not mentioned", model=embed_model
    # )
    #     Diet_embeddings= openai_client.embeddings.create(
    #     input=row.diet if row.diet else "Not mentioned" , model=embed_model
    # )
      
        
    food_embedding_to_upsert.append({'id': row.id , 'values': food_embeddings.data[0].embedding, 'metadata': {'RecipeName': row.recipename,'TotalTimeInMinutes': row.totaltimeinminutes,'Servings': row.servings,'Cuisine': row.cusine,'Diet': row.Diet, 'Course': row.Course,'YoutubeLink': row.youtubelink}})
        
# RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet

        # RecipeName_embedding_to_upsert.append({'id': row.id , 'values': RecipeName_embeddings.data[0].embedding, 'metadata': {'RecipeName': row.recipename,'TotalTimeInMinutes': row.totaltimeinminutes,'Servings': row.servings,'Cuisine': row.cusine,'Diet': row.Diet, 'Course': row.Course,'YoutubeLink': row.youtubelink}})
        
       
        


        # PrepTimeInMinutes_embedding_to_upsert.append({'id': row.id , 'values': PrepTimeInMinutes_embeddings.data[0].embedding, 'metadata': {'text': row.preptimeinminutes}})
        # index.upsert(index_name=index_name, vectors= PrepTimeInMinutes_embedding_to_upsert, namespace=("PrepTimeInMinutes"))

        # CookTimeInMinutes_embedding_to_upsert.append({'id': row.id , 'values': CookTimeInMinutes_embeddings.data[0].embedding, 'metadata': {'text': row.cooktimeinminutes}})
        # index.upsert(index_name=index_name, vectors= CookTimeInMinutes_embedding_to_upsert, namespace=("CookTimeInMinutes"))

        # TotalTimeInMinutes_embedding_to_upsert.append({'id': row.id , 'values': TotalTimeInMinutes_embeddings.data[0].embedding, 'metadata': {'text': row.totaltimeinminutes}})
        

        # Servings_embedding_to_upsert.append({'id': row.id , 'values': Servings_embeddings.data[0].embedding, 'metadata': {'text': row.servings}})
        

        # Cuisine_embedding_to_upsert.append({'id': row.id , 'values': Cuisine_embeddings.data[0].embedding, 'metadata': {'text': row.cuisine}})
        

        # Ingredients_embedding_to_upsert.append({'id': row.id , 'values':  Ingredients_embeddings.data[0].embedding, 'metadata': {'Ingredients': row.ingredients}})
        # Instructions_embedding_to_upsert.append({'id': row.id, 'values': Instructions_embeddings.data[0].embedding,'metadata': {'Instructions': row.instructions}})
        # Tags_embedding_to_upsert.append({'id': row.id , 'values': Tags_embeddings.data[0].embedding, 'metadata': {'text': row.tags}})
        

        # YouTubeLink_embedding_to_upsert.append({'id': f'recipie-{rand_chunk_code}', 'values': YouTubeLink_embeddings.data[0].embedding, 'metadata': {'text': row.youtubelink}})
        # index.upsert(index_name=index_name, vectors= YouTubeLink_embedding_to_upsert, namespace=("YouTubeLink"))

        # Course_embedding_to_upsert.append({'id':row.id , 'values':  Course_embeddings.data[0].embedding, 'metadata': {'text': row.course}})
        

        # Diet_embedding_to_upsert.append({'id': row.id , 'values': Diet_embeddings.data[0].embedding, 'metadata': {'text': row.diet}})
    print("sucessfully created embeddings")  
    # index.upsert(index_name=index_name, vectors=RecipeName_embedding_to_upsert, namespace=("RecipeName"))
    index.upsert(index_name=index_name, vectors=food_embedding_to_upsert, namespace=("Recipe"))
    # index.upsert(index_name=index_name, vectors=TotalTimeInMinutes_embedding_to_upsert, namespace=("TotalTimeInMinutes")) 
    # index.upsert(index_name=index_name, vectors=Servings_embedding_to_upsert, namespace=("Servings"))
    # index.upsert(index_name=index_name, vectors=Cuisine_embedding_to_upsert, namespace=("Cuisine"))
    # index.upsert(index_name=index_name, vectors=Ingredients_embedding_to_upsert, namespace=("Ingredients"))
    # index.upsert(index_name=index_name, vectors=Tags_embedding_to_upsert, namespace=("Tags"))
    # index.upsert(index_name=index_name, vectors=Course_embedding_to_upsert, namespace=("Course"))
    # index.upsert(index_name=index_name, vectors=Course_embedding_to_upsert, namespace=("Course"))
    # index.upsert(index_name=index_name, vectors= Diet_embedding_to_upsert, namespace=("Diet"))
    # index.upsert(index_name=index_name, vectors=Instructions_embedding_to_upsert, namespace=("Instructions"))
    print("sucessfully upserted")




fooddata=fetch_snowflake_data()
deleteAndCreatePineconeIndex()
create_embeddings_and_upsert(fooddata)