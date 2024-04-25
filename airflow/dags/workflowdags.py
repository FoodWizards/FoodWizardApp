from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from tasks import load_to_snowflake, clean_and_validate, create_embeddings, initial_setup
import constants

    
with DAG(
    dag_id='foodwizard_pipe',
    default_args={'start_date': days_ago(1),
                  'execution_timeout': timedelta(minutes=40)},
    schedule_interval="@monthly",  # Run once every month
    catchup=False
) as dag:
    
    initial_setup_task = PythonOperator(
        task_id=constants.TASK_INITIAL_SETUP_ID,
        python_callable=initial_setup.delete_prev_scraped_file,
        dag=dag
    )
    
    food_scraping_archanas = BashOperator(
        task_id=constants.TASK_FOOD_SCRAPE_ARCHANA_ID,
        bash_command='cd {} && python -m scrapy crawl foodspiderak'.format(constants.FOOD_SCRAPPER_SPIDER_PATH),
        dag=dag
    )

    food_scraping_ranveer = BashOperator(
        task_id=constants.TASK_FOOD_SCRAPE_RANVEER_ID,
        bash_command='cd {} && python -m scrapy crawl foodspiderrb'.format(constants.FOOD_SCRAPPER_SPIDER_PATH),
        dag=dag
    )

    clean_and_validate_task = PythonOperator(
        task_id=constants.TASK_CLEAN_VALIDATE_ID,
        python_callable=clean_and_validate.startCleanAndValidation,
        dag=dag
    )

    upload_to_snowflake = PythonOperator(
        task_id=constants.TASK_UPLOAD_TO_SNOWFLAKE_ID,
        python_callable=load_to_snowflake.start_upload,
        dag=dag
    )

    create_embeddings_task = PythonOperator(
        task_id=constants.TASK_CREATE_EMBEDDINGS_ID,
        python_callable=create_embeddings.fetchDataAndUpsert,
        dag=dag
    )
    
    initial_setup_task >> food_scraping_archanas >> food_scraping_ranveer >> clean_and_validate_task >> upload_to_snowflake >> create_embeddings_task