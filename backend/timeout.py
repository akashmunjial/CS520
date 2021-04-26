from functools import wraps
from signal import signal, alarm, SIGALRM

class Timeout(Exception):
    pass

def raise_timeout(*args):
    raise Timeout()

def timeout(*, seconds):
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                signal(SIGALRM, raise_timeout)
                alarm(seconds)
                result = func(*args, **kwargs)
                alarm(0)
                return result
            except Timeout:
                return None
        return wrapped_func
    return decorator
