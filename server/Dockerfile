FROM python:3.9.7-buster

WORKDIR /app

RUN apt-get update && apt-get install -y python3-opencv
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000
CMD [ "python3", "main.py"]