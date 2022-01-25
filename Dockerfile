# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get clean aa apt-get update

RUN apt-get update && apt-get install -y build-essential cmake
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libboost-all-dev

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -qqy x11-apps
ENV DISPLAY :1
CMD xeyes

RUN apt-get -y install xauth

COPY . .

#CMD [ "python3", "server.py"]