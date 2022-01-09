## Build the image torchserve locally before running this, cf github torchserve:
## https://github.com/pytorch/serve/tree/master/docker
FROM python:3.9.9-slim-buster
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y python3-distutils
RUN apt-get install -y wait-for-it

RUN useradd -m client
USER client
RUN pip3 install --upgrade pip
RUN pip install opencv-python
#We test opencv :
RUN python3 -c "import cv2"

COPY . /home/client

USER root
RUN chmod -R a+rw /home/client/
USER client

WORKDIR /home/client
RUN pip install -r requirements.txt

CMD ["wait-for-it", "server:8000", "--","python", "main.py"]

