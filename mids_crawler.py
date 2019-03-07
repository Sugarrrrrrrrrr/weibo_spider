from utils import mids_crawl
from logging_config import setup_logging
from settings import logging_config
from settings import *
import time
import logging


def run(n=10000, status=STATUS_OUTSTANDING):
    logger = logging.getLogger('main')

    begin_time = time.asctime()
    mids_crawl(n, status)
    end_time = time.asctime()

    logger.info('mids_crawl:\n%s\n%s\n----------', begin_time, end_time)


if __name__ == '__main__':
    setup_logging(logging_config)
    # run(100, status=STATUS_NEW_ADDED)
    run(1)
