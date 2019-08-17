FROM ubuntu:18.04

RUN apt update
#RUN apt install inetutils-ping net-tools -y

RUN apt install python3 python3-pip vim -y
RUN pip3 install pika pymongo
#RUN pip3 install tensorflow numpy torch opencv_python 

#COPY ./sender.py /sender.py
#CMD python3 -u /sender.py

COPY ./ui_server.py /ui_server.py
COPY ./index.html /index.html
CMD python3 -u /ui_server.py

