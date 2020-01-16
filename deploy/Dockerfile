#Context of this file should be ../
FROM python:3.6

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./hakaze ./hakaze
COPY ./static ./static
COPY ./templates ./templates
COPY ./main.py ./main.py


CMD ["python", "main.py"]
