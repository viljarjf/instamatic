from functools import wraps
from logging import Logger


def get_instance_method_logger(logger: Logger):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            msg = (
                func.__name__
                + "("
                + ", ".join(
                    [str(arg) for arg in args[1:]]
                    + [f"{key}={val}" for key, val in kwargs.items()]
                )
                + ")"
            )
            out = func(*args, **kwargs)
            msg += ": " + str(out)
            logger.debug(msg)
            return out

        return inner

    return wrapper
