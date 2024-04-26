# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

ADD kafka_python-2.0.3.dev0-py2.py3-none-any.whl .

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN python -m pip install kafka_python-2.0.3.dev0-py2.py3-none-any.whl

EXPOSE 8000

COPY ./backend /code/app

COPY ./backend/script.sh .

RUN chmod +x script.sh

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
ENTRYPOINT ["./script.sh"]
# CMD ["sh", "/home/script.sh"]