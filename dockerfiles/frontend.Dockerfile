FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY ./frontend /code

ENTRYPOINT ["streamlit", "run", "/code/app.py", "--server.port=8501", "--server.address=0.0.0.0"]