FROM python:3.9.6-slim-buster

ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

ADD . /app/

ENTRYPOINT [ "python", "telethon_app.py" ]