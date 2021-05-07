FROM python:latest

RUN mkdir usr/app
WORKDIR usr/app 

COPY . .

RUN pip install -r requirments.txt 

CMD python app.py 
