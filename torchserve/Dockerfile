## Build the image torchserve locally before running this, cf github torchserve:
## https://github.com/pytorch/serve/tree/master/docker
FROM pytorch/torchserve:latest
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y python3-distutils

USER model-server
RUN pip3 install --upgrade pip
RUN pip install torch-model-archiver
RUN pip install opencv-python
#We test opencv :
RUN python3 -c "import cv2"

COPY . /home/model-server

USER root
RUN chmod -R a+rw /home/model-server/
USER model-server

RUN pip install -r /home/model-server/yolov5_torchserve/ressources/yolov5/requirements.txt
EXPOSE 8080 8080
ENV PYTHONPATH "${PYTHONPATH}:/home/model-server/yolov5_torchserve/ressources/yolov5/"
WORKDIR /home/model-server
RUN sh create_model.sh
##CMD [ "torchserve", "--start", "--model-store", "model_store", "--models", "'scalenet.mar mask.mar yolov5.mar'" ]
CMD ["/bin/sh", "start.sh"]

