#Context of this file should be ../
FROM nginx

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./hakaze ./hakaze
COPY ./main.py ./main.py

CMD ["python", "main.py"]
