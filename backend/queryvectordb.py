import openai
from openai import OpenAI
import os
from pinecone import Pinecone, PodSpec, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# The recipe name is "{row.recipename}". 
#         It has a preparation time of {row.preptimeinminutes} minutes, a cook time of "{row.cooktimeinminutes}" minutes, and a total time of "{row.totaltimeinminutes}" minutes. This recipe serves "{row.servings}" people and belongs to 
#         the "{row.cuisine}" cuisine category. This recipe falls under the "{row.course}" course category and is suitable for a "{row.diet}" diet.  The ingredients include "{row.ingredients}"
#         The instructions involve "{row.instructions}". Additionally, a YouTube link to a video demonstrating the recipe is provided:{row.youtubelink}"""
    

#     recipe_name(don’t infer): 
# ingredients:
# cooking_time(in minutes):
# cuisine: 
# servings_needed: 
# course:
# meal_type:
# cooking_instructions: 
# additional_tags(useful tags based on context): 
# diet(can be vegan, satvik, jain, no meat, pescetarian): 




def _fetchAnswerFromGPT(contextStr):
    prompt = f"""
            RecipeName (don’t infer): 
            TotalTimeInMinutes(in minutes):
            Ingredients:
            Servings:
            Cuisine: 
            Diet(can be vegan, satvik, jain, no meat, pescetarian):
            Course(can be lunch,dinner, breakfast,sidedish, main course, starter):
            Tags(useful tags based on context):
            Instructions:

           

            Fill the above from the context given below. If you are not sure(probability < 50%) then fill the field with None.
            Following is the context paragraph:
            {contextStr}
    
            """
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": """You are a helpful and smart bot who tries to fill in the template given below by the context given by user. """},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content




# initialize connection to pinecone
index_name = 'fooddata'

api_key = os.getenv("PINECONE_API_KEY")
print(api_key)
pinecone_client = Pinecone(api_key=api_key)
index = pinecone_client.Index(index_name)  

def _getEmbeddingsForRecipe(text):
   
    embed_model = "text-embedding-3-small"
    text_embeddings= openai_client.embeddings.create(
        input=text if text else "Not mentioned" , model=embed_model
    ).data[0].embedding
    # print(text_embeddings)
    res = index.query(
        vector=text_embeddings,
        top_k=3,
        include_values=False,
        namespace=("Recipe")
    )
    idList = []
    for match in res.matches:
        idList.append(match.id)
    return idList

def _getContextFromMatchingKnowledgeEmbeddings(indexes):
    res = index.fetch(ids=indexes, namespace=("Recipe"))
    contextStr = []
    for key, match in res.vectors.items():
        # match.metadata['text']
        contextStr.append({'RecipeName': match.metadata['RecipeName'],'TotalTimeInMinutes': match.metadata['TotalTimeInMinutes'],
                           'Servings': match.metadata['Servings'],'Cuisine': match.metadata['Cuisine'],'Diet': match.metadata['Diet'], 'Course': match.metadata['Course'],
                           'YoutubeLink': match.metadata['YoutubeLink'], 'CookTimeInMinutes': match.metadata['CookTimeInMinutes'],
                           'PrepTimeInMinutes':match.metadata['PrepTimeInMinutes'],'Instructions':match.metadata['Instructions'],
                           'Ingredients':match.metadata['Ingredients']})
    return contextStr

# text = """   
#      I want something for Dinner. I have  Mushroom, Paneer, Brinjal, prawn. I have 20 mins.
#         """

def getrecommendedrecipes(text):
    response=_fetchAnswerFromGPT(text)
    print(response)
    list=_getEmbeddingsForRecipe(text)
    print(list)
    data =_getContextFromMatchingKnowledgeEmbeddings(list)
    return data




