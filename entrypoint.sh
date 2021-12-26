#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Waiting for elasticsearch..."
while ! nc -z es 9200; do
  sleep 0.1
done
echo "Elasticsearch started"

uvicorn main:app --host 0.0.0.0 --port 8000
