FROM ubuntu:18.04

RUN apt update
#RUN apt install inetutils-ping net-tools -y

RUN apt install python3 python3-pip vim -y
RUN pip3 install pika pymongo
#RUN pip3 install tensorflow numpy torch opencv_python 

COPY ./worker.py /worker.py

CMD python3 -u /worker.py
#CMD ping rabbitmq

