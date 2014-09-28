from functools import wraps

__author__ = 'sikamedia'
__Date__ = '2014-09-28'


def encrypt_wallet(func):
    pass


def unlock_wallet(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        x = False

        if x:
            return func(*args, **kwargs)
        else:
            return "you are not allowed to do stuff"
    return wrapper
