# syntax=docker/dockerfile:1

FROM python:3.7

WORKDIR /app

RUN apt update -y
RUN apt-get update -y
# RUN apt-get install mysql-server -y
# RUN apt-get install libmysqlclient-dev -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "ETL_process.main"]