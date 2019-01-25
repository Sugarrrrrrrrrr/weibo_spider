from utils import add_timestamp_for_mblogs
import logging
import time


def run(n=10000, max_times=0):
    logger = logging.getLogger('main')

    begin_time = time.asctime()
    add_timestamp_for_mblogs(n, max_times)
    end_time = time.asctime()

    logger.info('add_timestamp_for_mblogs:\n%s\n%s\n----------', begin_time, end_time)
    # print('add_timestamp_for_mblogs:\n%s\n%s\n----------' % (begin_time, end_time))


if __name__ == '__main__':

    n = 20
    max_times = 10
    run(n, max_times)

