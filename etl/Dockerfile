FROM python:3.9
RUN  apt-get update && apt-get install -y netcat && pip install --upgrade pip

WORKDIR /etl

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["sh", "entrypoint.sh"]