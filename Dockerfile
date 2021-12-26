FROM python:3.9
RUN  apt-get update && apt-get install -y netcat && pip install --upgrade pip

WORKDIR /app

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src/ .

ENTRYPOINT ["sh", "entrypoint.sh"]