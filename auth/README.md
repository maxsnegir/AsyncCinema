# AuthService

### Описание
Сервис для авторизации пользователей в онлайн кинотеатре

### Технологии

- Python 3.8
- Flask
- Postgres 12
- Docker
- Redis

## Запуск проекта

_Все команды должны выполняться в главной директории проекта._

1. Создайте файл **.env** с переменными окружения для работы проекта (пример в файле **.env.template**):

2. Убедитесь, что у вас
   установлен и запущен [Docker](https://www.docker.com/products/docker-desktop)
3. Запустите проект командой:

```bash
docker-compose up --build 
```

4. Создание супер пользователя
```
docker exec -it auth python commands.py create-superuser <login> <email address> <password>
```

### Запуск тестов
1. Перейдите в директорию auth
2. Выполните команду:
```
docker-compose -f docker-compose.test.yaml up --build
```
