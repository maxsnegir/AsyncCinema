FROM python:3.9 as base
RUN  apt-get update && pip install --upgrade pip
WORKDIR /auth
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .


FROM base as prod
CMD flask db upgrade && python commands.py create-base-roles && python commands.py runserver

FROM base as tests
CMD pytest -v tests/functional/src
