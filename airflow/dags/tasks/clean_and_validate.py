import pandas as pd
from tasks.validationclass import ContentClass
import csv
import os
import constants
import string
import random

def _write_to_csv(obj_list):
    fieldnames = list(ContentClass.schema()["properties"].keys())
    directory = constants.LOCAL_DATA_PATH
    filename = "clean_data.csv"

    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_STRINGS)
        writer.writeheader()
        for obj in obj_list:
            writer.writerow(obj.model_dump())
        return filepath

def _startValidation(filePath, ti):
    df = pd.read_csv(filePath)
    validate_record_count = 0
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
    filtered_df.loc[:, 'Ingredients'] = filtered_df['Ingredients'].fillna(str("")).astype(str)
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
    
    if validate_record_count == filtered_df.shape[0]:
        print("Successfully validated")
    else:
        print("Validation failed in some records. Please fix and retry")
    cleaned_file_path = _write_to_csv(contentinstance_list)
    ti.xcom_push(key=constants.XKEY_SCRAPED_CLEANED_FILE_PATH, value=cleaned_file_path)

def startCleanAndValidation(**kwargs):
    ti = kwargs['ti']
    _startValidation(filePath=constants.TEMP_SCRAPED_FILE_PATH, ti=ti)
    