from utils import mblogs_crawl
import time


def run():
    begin_time = time.asctime()
    mblogs_crawl()
    end_time = time.asctime()

    print('mblogs_crawl:')
    print(begin_time)
    print(end_time)
    print('----------')


if __name__ == '__main__':
    n = 2
    for i in range(n):
        run()