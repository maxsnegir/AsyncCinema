# AsyncCinema

### Описание
Групповая проектная работа 4 спринта по реализации асинхронного API для кинотеатра

### Технологии

- Python 3.8
- FastAPI 0.61.1
- Postgres 12
- Docker
- ElasticSearch
- Redis

### Клонирование репозитория

*Через http протокол:*

```bash
git clone https://github.com/maxsnegir/AsyncCinema.git
```

*Через ssh протокол:*

```bash
git clone git@github.com:maxsnegir/AsyncCinema.git
```

## Запуск проекта

_Все команды должны выполняться в главной директории проекта._

1. Создайте файл **.env** с переменными окружения для работы проекта (пример в файле **.env.template**):

2. Убедитесь, что у вас
   установлен и запущен [Docker](https://www.docker.com/products/docker-desktop)
3. Запустите проект командой:

```bash
docker-compose up --build 
```

Проект запущен, документация API доступна по адресу http://localhost:8000/api/openapi



