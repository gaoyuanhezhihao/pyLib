import logging
from datetime import datetime
from timeit import default_timer as timer
from functools import wraps

logging.basicConfig(format='%(asctime)s.%(msecs)04d %(levelname)s [%(funcName)s] %(message)s',
                    level=logging.INFO,
                    datefmt='%H:%M:%S')
logger = logging.getLogger('DirectoryCache')
handler = logging.FileHandler('DirectoryCache_%s.log' % datetime.now().ctime().replace(' ', '_'))
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d thread-%(thread)d %(levelname)s [%(funcName)s] %(message)s', datefmt='%H:%M:%S')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        logger.debug("{} ran in {}ms".format(func.__name__, (end - start)*1000))
        return result
    return wrapper
