from datetime import datetime
from hashlib import md5


def random_string(length: int = 10) -> str:
    """
    Generate a random string.
    :param length: length of the string, max 32
    :return: random string
    """
    length = min(max(1, length), 32)
    return md5(str(datetime.now()).encode()).hexdigest()[:length]
