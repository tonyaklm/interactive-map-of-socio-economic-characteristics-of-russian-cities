FROM python:3.10-slim

WORKDIR .

COPY user_service/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
RUN apt-get -y update; apt-get -y install curl

COPY user_service/src/ /

CMD ["python", "main.py"]