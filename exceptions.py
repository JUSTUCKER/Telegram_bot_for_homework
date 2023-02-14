class InvalidResponseCode(Exception):
    """Не верный код ответа."""

    pass


class EmptyResponseFromAPI(Exception):
    """Пустой ответ от API."""

    pass
