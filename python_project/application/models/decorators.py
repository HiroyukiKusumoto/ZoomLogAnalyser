import threading
from contextlib import redirect_stdout
import os


def th_deco(func):
    def wrapper(*args, **kwargs):
        this_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        result = this_thread.start()
        return result
    return wrapper


def redirect_deco(func):
    def wrapper(*args, **kwargs):
        with redirect_stdout(open(os.devnull, "w")):
            result = func(*args, **kwargs)
        return result
    return wrapper
