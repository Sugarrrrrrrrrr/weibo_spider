from utils import mids_crawl
from logging_config import setup_logging
from settings import logging_config
import time
import logging


def run():
    logger = logging.getLogger('main')

    begin_time = time.asctime()
    mids_crawl()
    end_time = time.asctime()

    logger.info('mids_crawl:\n%s\n%s\n----------', begin_time, end_time)


if __name__ == '__main__':
    setup_logging(logging_config)
    run()
