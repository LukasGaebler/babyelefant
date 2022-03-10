FROM python:3.9.7-buster

WORKDIR /app

RUN apt-get update && apt-get install -y python3-opencv
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase

COPY requirements-cpu.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . .

RUN usermod -a -G video root

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:8000", "run:app"]      
#CMD [ "python3","-u", "/app/run.py"]