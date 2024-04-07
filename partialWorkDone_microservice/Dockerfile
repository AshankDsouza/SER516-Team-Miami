
FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app

EXPOSE 8080

ENV TAIGA_URL=https://api.taiga.io/api/v1

WORKDIR /app/Backend

CMD ["flask", "--app", "flaskProject/main", "run", "--debug", "--host=0.0.0.0"]
