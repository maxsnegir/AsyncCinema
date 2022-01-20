FROM python:3.9
RUN  apt-get update && pip install --upgrade pip
WORKDIR /tests
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .