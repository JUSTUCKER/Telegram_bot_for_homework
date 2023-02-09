class TelegramError(Exception):
    """Проблема со стороны Telegram."""

    pass


class APIResponseError(Exception):
    """Ошибка ответа от API."""

    pass
