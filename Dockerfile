FROM python:3.9.6-slim-buster

ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN apt-get update
RUN apt-get install -y --reinstall \
    ffmpeg \
    libsm6 \
    libxext6 \
    build-essential \
    gcc \
    libleptonica-dev \
    tesseract-ocr \
    libtesseract-dev \
    python3-pil \
    tesseract-ocr-eng \
    tesseract-ocr-script-latn \
    tesseract-ocr-ukr

RUN pip install -r requirements.txt

ADD . /app/

RUN apt-get install tesseract-ocr-ukr

ENTRYPOINT [ "python", "telethon_app.py" ]