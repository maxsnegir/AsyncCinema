#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Загрузка данных из sqlite в psql"
cd sqlite_to_postgres
python load_data.py
echo "Загрузка завершена"

echo "Waiting for elasticsearch..."
while ! nc -z elasticsearch 9200; do
  sleep 0.1
done
echo "Elasticsearch started"

cd ..
echo "Загрузка данных в Elasticsearch"
python main.py
echo "Загрузка завершена"
