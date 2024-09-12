FROM python:3.9.6-slim-buster

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


ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD . /app/

WORKDIR /app

ENTRYPOINT [ "python", "lightsoff/application.py" ]