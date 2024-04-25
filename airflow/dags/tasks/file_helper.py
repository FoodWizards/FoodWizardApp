import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
import constants
import random
from urllib.parse import urlparse
from pathlib import Path


# Load environment variables from .env file
load_dotenv()

# Access environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def _upload_to_s3(local_file_path, bucket_name, s3_file_path):    
    s3_client.upload_file(local_file_path, bucket_name, s3_file_path)

def _generate_random_string() -> str:
    return ''.join(random.choice('0123456789abcdef') for i in range(16))

def _get_path_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip('/')

def download_and_initial_setup(**kwargs):
#    pdf_url = "https://bigdataia-team7.s3.amazonaws.com/2024-l1-topics-combined-2.pdf"
    pdf_url = kwargs["dag_run"].conf["uploaded_file"]
    print('Selected pdf:' + pdf_url)
    ti = kwargs['ti']
    local_folder_name = _generate_random_string()
    local_folder_path = os.path.join(constants.LOCAL_DATA_PATH, local_folder_name)
    local_file_path = os.path.join(local_folder_path, os.path.basename(pdf_url))
    Path(local_folder_path).mkdir(parents=True, exist_ok=True)

    pdf_path = _get_path_from_url(pdf_url)
    print(f'pdf path {pdf_path}')
    print(f'pdf local file path {local_file_path}')
    s3_client.download_file(S3_BUCKET_NAME, pdf_path, local_file_path)

    ti.xcom_push(key=constants.XKEY_TEMP_FOLDER_NAME, value=local_folder_name)
    ti.xcom_push(key=constants.XKEY_TEMP_FOLDER_PATH, value=local_folder_path)
    ti.xcom_push(key=constants.XKEY_S3_PDF_LINK, value=pdf_url)

def _build_s3_link(s3_path):
    return f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_path}'

def upload_files(**kwargs):  
    ti = kwargs['ti']
    temp_xml_file_path = ti.xcom_pull(key=constants.XKEY_TEMP_XML_FILE_PATH, task_ids=constants.TASK_GROBID_PROCESS_ID) 
    temp_txt_file_path = ti.xcom_pull(key=constants.XKEY_TEMP_TXT_FILE_PATH, task_ids=constants.TASK_XML_TO_TEXT_ID) 
    temp_folder_name = ti.xcom_pull(key=constants.XKEY_TEMP_FOLDER_NAME, task_ids=constants.TASK_SETUP_ID) 
    
    s3_path_prefix = os.path.join('processed_data', temp_folder_name)

    _upload_to_s3(temp_xml_file_path, S3_BUCKET_NAME, os.path.join(s3_path_prefix, os.path.basename(temp_xml_file_path)) )
    _upload_to_s3(temp_txt_file_path, S3_BUCKET_NAME, os.path.join(s3_path_prefix, os.path.basename(temp_txt_file_path)) )
    
    ti.xcom_push(key=constants.XKEY_S3_XML_LINK, value=_build_s3_link(os.path.join(s3_path_prefix, os.path.basename(temp_xml_file_path))) )
    ti.xcom_push(key=constants.XKEY_S3_TXT_LINK, value=_build_s3_link(os.path.join(s3_path_prefix, os.path.basename(temp_txt_file_path))) )
