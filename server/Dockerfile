FROM pytorch/pytorch:1.7.1-cuda11.0-cudnn8-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y python3-opencv
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN usermod -a -G video root

EXPOSE 8000
CMD [ "python3", "main.py"]