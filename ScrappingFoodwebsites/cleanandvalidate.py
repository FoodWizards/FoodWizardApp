
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from validationclass import ContentClass
import csv
import json
import re
import os

from pydantic import BaseModel
import string
import random

df = pd.read_csv("/Users/rutujakute/Documents/ScrappingFoodwebsites/foodscrapper/foodscrapper/spiders/scraped_data.csv")
validate_record_count =0
# 
value_to_remove = 'CookTimeInMinutes'

# Filter out rows with the specified value in column 'B'
filtered_df = df[df['CookTimeInMinutes'] != value_to_remove]
filtered_df = filtered_df.replace(',', '', regex=True)

filtered_df.loc[:, 'CookTimeInMinutes'] = filtered_df['CookTimeInMinutes'].fillna(int()).astype(int)
filtered_df.loc[:, 'TotalTimeInMinutes'] = filtered_df['TotalTimeInMinutes'].fillna(int()).astype(int)
filtered_df.loc[:, 'PrepTimeInMinutes'] = filtered_df['PrepTimeInMinutes'].fillna(int()).astype(int)
filtered_df.loc[:, 'Servings'] = filtered_df['Servings'].fillna(int()).astype(int)
filtered_df.loc[:, 'Course'] = filtered_df['Course'].fillna(str("")).astype(str)
filtered_df.loc[:, 'Cuisine'] = filtered_df['Cuisine'].fillna(str("")).astype(str)
filtered_df.loc[:, 'Diet'] = filtered_df['Diet'].fillna(str("")).astype(str)
filtered_df.loc[:, 'Ingredients'] = filtered_df['Diet'].fillna(str("")).astype(str)
filtered_df.loc[:, 'Instructions'] = filtered_df['Instructions'].fillna(str("")).astype(str)
filtered_df.loc[:, 'YouTubeLink'] = filtered_df['YouTubeLink'].fillna(str("")).astype(str)
filtered_df.loc[:, 'Tags'] = filtered_df['Tags'].fillna(str("")).astype(str)

contentinstance_list =[]
for i, row in filtered_df.iterrows():
    characters = string.ascii_letters + string.digits
    rand_chunk_code = ''.join(random.choices(characters, k=3))
    try:
        obj = ContentClass(ID = f'recipie-{rand_chunk_code}',CookTimeInMinutes= row.CookTimeInMinutes,Course= str(row.Course), Cuisine=str(row.Cuisine), Diet= str(row.Diet), Ingredients= str(row.Ingredients),
        Instructions= str(row.Instructions), PrepTimeInMinutes= row.PrepTimeInMinutes, RecipeName= str(row.RecipeName), Servings= row.Servings, Tags=str(row.Tags),
        TotalTimeInMinutes= row.TotalTimeInMinutes, YouTubeLink=str(row.YouTubeLink))
        contentinstance_list.append(obj)
        validate_record_count += 1
    except Exception as ex:
        print(ex)

def write_to_csv(obj_list):
    fieldnames = list(ContentClass.schema()["properties"].keys())
    directory = 'clean_csv/'

# Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open("clean_csv/clean_data.csv", "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_STRINGS)
        writer.writeheader()
        for obj in obj_list:
            writer.writerow(obj.model_dump())

if validate_record_count == filtered_df.shape[0]:
    print("Successfully validated")
    write_to_csv(contentinstance_list)
else:
    print("Validation failed in some records. Please fix and retry")