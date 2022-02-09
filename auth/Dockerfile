FROM python:3.9
RUN  apt-get update && pip install --upgrade pip

WORKDIR /auth

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD flask db upgrade && python commands.py create-base-roles && python commands.py runserver