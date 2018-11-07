from utils import run_with_threads, update_user_data_and_mids_queue
from settings import *
import time


def run():
    uids = list()
    with open('uids.txt', 'r') as f:
        for line in f:
            uids.append(line.strip())

    begin_time = time.asctime()
    run_with_threads(update_user_data_and_mids_queue, uids, max_thread_num_for_mids_crawl)
    end_time = time.asctime()

    print('mids_crawl:')
    print(begin_time)
    print(end_time)
    print('----------')


if __name__ == '__main__':
    run()
