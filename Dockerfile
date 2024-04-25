FROM apache/airflow:2.9.0b2-python3.12
ADD requirements.txt .
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt