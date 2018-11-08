import mids_crawler
import mblogs_crawler
from utils import *
import time

if __name__ == '__main__':

    while True:
        try:
            print('mids_crawler.running ----------------------------------------')
            mids_crawler.run()

            # mblogs crawler
            count = get_outstanding_mids_num()
            print('outstanding mids: {}'.format(count))
            if count != 0:
                n = int((count-1)/10000) + 1
                print('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    mblogs_crawler.run()

            # print('handle_mids_with_status_processing_exception ----------------')
            # mongoctl.handle_mids_with_status_processing_exception()

            print('handle_status_with_status_error_exception -------------------')
            mongoctl.handle_mids_with_status_error_exception()

            # repeat mblogs crawler
            count = get_outstanding_mids_num()
            print('outstanding mids to retry: {}'.format(count))
            if count != 0:
                n = int((count - 1) / 10000) + 1
                print('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    mblogs_crawler.run()

        except Exception as e:
            print(time.asctime())
            print(e)

        print('\n##### sleeping #####\n\n')
        time.sleep(4*60*60)
        print('##### working  #####')

