
class TestErrors:
    WRONG_STATUS = "Неправильный статус ответа"
    WRONG_LEN = "Неправильное количество элементов"
    WRONG_RESPONSE_BODY = "Неправильный тип данных в ответе"
    WRONG_GTE_PAGE_SIZE = "Неправильный статус ответа для размера страницы со значением > 1000"
    WRONG_LTE_PAGE_SIZE = "Неправильный статус ответа для размера страницы со значением == 0"

    REDIS_404 = "Отсутствуют данные в redis"