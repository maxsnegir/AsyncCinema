FROM python:3.9
RUN  apt-get update && apt-get install -y netcat && pip install --upgrade pip

WORKDIR /api

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]