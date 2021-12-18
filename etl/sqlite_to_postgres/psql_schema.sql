-- Создание отдельной схемы
CREATE SCHEMA IF NOT EXISTS content;
-- SET search_path TO content, public;
-- Добавление модуля для генерации uuid, если его нет
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создаем таблицу фильма
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating REAL,
    type VARCHAR(60) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу жанра
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу персоны
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу связывающую жанр с фильмом
CREATE TABLE IF NOT EXISTS content.genre_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
    genre_id uuid REFERENCES content.genre (id) NOT NULL,
    created_at timestamp with time zone
);

-- Создаем таблицу связывающую персону с фильмом
CREATE TABlE IF NOT EXISTS content.person_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
    person_id uuid REFERENCES content.person (id) NOT NULL,
    role VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE
);

-- Устанавливаем индекс, для невозможности присвоению фильму несколько одинаковых жанров
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ON content.genre_film_work (film_work_id, genre_id);
-- Устанавливаем индекс, для невозможности присвоения фильму актеров, уже снимающихся в этой роли
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
