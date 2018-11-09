from utils import mblogs_crawl
from logging_config import setup_logging
from settings import logging_config
import logging
import time


def run():
    logger = logging.getLogger('main')

    begin_time = time.asctime()
    mblogs_crawl()
    end_time = time.asctime()

    logger.info('mblogs_crawl:\n%s\n%s\n----------', begin_time, end_time)


if __name__ == '__main__':
    setup_logging(logging_config)

    n = 2
    for i in range(n):
        run()