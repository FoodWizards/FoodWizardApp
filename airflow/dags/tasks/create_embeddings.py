from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
from openai import OpenAI
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.engine import URL
import constants

load_dotenv(verbose=True, override=True)


def _fetch_snowflake_data():
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
    query = f"SELECT * FROM {os.getenv('SNOWFLAKE_TABLE')}"
  
    result=connection.execute(query)
    los_data = result.fetchall()
    connection.close()
    return los_data

def _deleteAndCreatePineconeIndex():
    pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # check if index already exists (it shouldn't if this is first time)
    if len(pinecone_client.list_indexes()) > 0:
        pinecone_client.delete_index(name=pinecone_client.list_indexes()[0].name)
    
    # Create index
    pinecone_client.create_index(
        constants.OPENAI_INDEX_NAME,
        dimension=1536,
        metric='dotproduct',
        spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1")
    )
    print("Deleted previous pinecone index and created new one")

def _create_embeddings_and_upsert(fooddata):
    pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    embed_model = "text-embedding-3-small"
    food_embedding_to_upsert =[]
    index = pinecone_client.Index(constants.OPENAI_INDEX_NAME)   
   
    df = pd.DataFrame(fooddata)
    for i, row in df.iterrows():
        input = f"""The recipe name is "{row.recipename}". 
        It has a preparation time of {row.preptimeinminutes} minutes, a cook time of "{row.cooktimeinminutes}" minutes, and a total time of "{row.totaltimeinminutes}" minutes. This recipe serves "{row.servings}" people and belongs to 
        the "{row.cuisine}" cuisine category. This recipe falls under the "{row.course}" course category and is suitable for a "{row.diet}" diet.  The ingredients include "{row.ingredients}"
        The instructions involve "{row.instructions}". Additionally, a YouTube link to a video demonstrating the recipe is provided:{row.youtubelink}"""
  
        food_embeddings = openai_client.embeddings.create(
            input=input if input else "Not mentioned" , model=embed_model
        )
        print(f"Uploaded embedding {i}")

        food_embedding_to_upsert.append({'id': row.id , 'values': food_embeddings.data[0].embedding, 'metadata':{'RecipeName': row.recipename,'TotalTimeInMinutes': row.totaltimeinminutes,'Servings': row.servings,'Cuisine': row.cuisine,'Diet': row.diet, 'Course': row.course,'YoutubeLink': row.youtubelink, 'CookTimeInMinutes': row.cooktimeinminutes,'PrepTimeInMinutes':row.preptimeinminutes,'Instructions':row.instructions,'Ingredients':row.ingredients}})
       
    # RecipeName	PrepTimeInMinutes	CookTimeInMinutes	TotalTimeInMinutes	Servings	Cuisine	Ingredients	Instructions	Tags	YouTubeLink	Course	Diet
    print("Sucessfully created all embeddings")  
    def chunk_list(lst, batch_size):
        """Chunk a list into batches of specified size."""
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]

    # Chunking into batches of 100
    batched_list = list(chunk_list(food_embedding_to_upsert, 100))

    # Accessing all chunks
    count = 0
    for chunk in batched_list:
        count += 1
        index.upsert(index_name=constants.OPENAI_INDEX_NAME, vectors=chunk, namespace=("Recipe"))
        print(f"Chunk upserted {count}")
    print("successfully upserted all")

def fetchDataAndUpsert(**kwargs):
    fooddata = _fetch_snowflake_data()
    _deleteAndCreatePineconeIndex()
    _create_embeddings_and_upsert(fooddata)