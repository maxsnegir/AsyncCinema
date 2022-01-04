from functools import wraps
from time import sleep

import psycopg2
from elasticsearch import ElasticsearchException

from config import logger


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания
    (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            t = start_sleep_time
            errors_count = 0
            max_errors_count = 5
            while True:
                try:
                    return func(*args, **kwargs)

                except ElasticsearchException as ex:
                    msg = f'Ошибка при загрузке данных в Elasticsearch ex={ex}'
                except psycopg2.Error as ex:
                    msg = f'Ошибка при получении данных из базы ex={ex}'
                except Exception as ex:
                    msg = f'Непредвиденная ошибка ex={ex}'

                if t < border_sleep_time:
                    t = t * factor
                if t >= border_sleep_time:
                    t = border_sleep_time

                logger.error(f"{msg}, спим {t} сек")
                errors_count += 1
                sleep(t)

                if errors_count > max_errors_count:
                    logger.error(f"Превышено максимальное количество ошибок при выполнении функции {func.__name__}")
                    break

        return inner
    return func_wrapper
