import random
import uuid


def gen_film_data(count):

    film_list = []
    text_const = "Lorem ipsum dolor sit amet"

    for _ in range(count):
        film_id = uuid.uuid4()
        film = {
            "uuid": film_id,
            "title": text_const,
            "imdb_rating": round(random.uniform(0, 10), 1),
            "description": text_const,
            "genre": [{"name": text_const, "uuid": uuid.uuid4()} for _ in range(random.randint(1, 5))],
            "actors": [{"full_name": text_const, "uuid": uuid.uuid4()} for _ in range(random.randint(1, 5))],
            "directors": [{"full_name": text_const, "uuid": uuid.uuid4()} for _ in range(random.randint(1, 5))],
            "writers": [{"full_name": text_const, "uuid": uuid.uuid4()} for _ in range(random.randint(1, 5))],
        }
        film_list.append(film)

    return film_list
