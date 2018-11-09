import mids_crawler
import mblogs_crawler
from utils import *
from logging_config import setup_logging
import time

if __name__ == '__main__':

    setup_logging(logging_config)
    logger = logging.getLogger('main')

    while True:
        try:
            logger.info('mids_crawler.running ----------------------------------------')
            mids_crawler.run()

            # mblogs crawler
            count = get_outstanding_mids_num()
            logger.info('outstanding mids: {}'.format(count))
            if count != 0:
                n = int((count-1)/10000) + 1
                logger.info('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    mblogs_crawler.run()

            # print('handle_mids_with_status_processing_exception ----------------')
            # mongoctl.handle_mids_with_status_processing_exception()

            logger.info('handle_status_with_status_error_exception -------------------')
            mongoctl.handle_mids_with_status_error_exception()

            # repeat mblogs crawler
            count = get_outstanding_mids_num()
            logger.info('outstanding mids to retry: {}'.format(count))
            if count != 0:
                n = int((count - 1) / 10000) + 1
                logger.info('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    mblogs_crawler.run()

        except Exception as e:
            logger.info(time.asctime())
            logger.info(e)

        logger.info('\n##### sleeping #####\n\n')
        time.sleep(4*60*60)
        logger.info('##### working  #####')

