import mids_crawler
import mblogs_crawler
import timestamp_add
from utils import *
from logging_config import setup_logging
import time
import datetime

if __name__ == '__main__':

    setup_logging(logging_config)
    logger = logging.getLogger('main')

    # config
    mongoctl.set_config_mainloop(True)

    while True:
        try:
            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            logger.info('##### working  #####')
            begin_time = datetime.datetime.now()

            logger.info('new uids added ----------------------------------------------')
            mids_crawler.run(1000, status=STATUS_NEW_ADDED)
            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            count = get_outstanding_uids_num()
            logger.info('outstanding uids: {}'.format(count))
            if count > 50000:
                count = 50000
            if count != 0:
                n = int((count-1)/10000) + 1
                logger.info('mids_crawler.running ----------------------------------------')
                for i in range(n):
                    # begin stop check
                    if not mongoctl.get_config_mainloop():
                        break
                    # finish stop check
                    logger.info('# %d #' % (i + 1))
                    mids_crawler.run()
                    pass

            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            # mblogs crawler
            count = get_outstanding_mids_num()
            logger.info('outstanding mids: {}'.format(count))
            if count != 0:
                n = int((count-1)/10000) + 1
                logger.info('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    # begin stop check
                    if not mongoctl.get_config_mainloop():
                        break
                    # finish stop check
                    logger.info('# %d #' % (i+1))
                    mblogs_crawler.run()
                    pass

            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            # print('handle_mids_with_status_processing_exception ----------------')
            # mongoctl.handle_mids_with_status_processing_exception()

            logger.info('handle_status_with_status_error_exception -------------------')
            mongoctl.handle_mids_with_status_error_exception()
            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            # repeat mblogs crawler
            count = get_outstanding_mids_num()
            logger.info('outstanding mids to retry: {}'.format(count))
            if count != 0:
                n = int((count - 1) / 10000) + 1
                logger.info('mblogs_crawler.running --------------------------------------')
                for i in range(n):
                    # begin stop check
                    if not mongoctl.get_config_mainloop():
                        break
                    # finish stop check
                    mblogs_crawler.run()

            # add created_timestamp for mblogs
            timestamp_add.run()
            pass

            end_time = datetime.datetime.now()

            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            sleep_time = 6 * 60 * 60 - (end_time - begin_time).total_seconds()
            if sleep_time < 0:
                sleep_time = 0.5 * 60 * 60

            logger.info('\ncost: %s\n##### sleeping #####\n\n' % str(end_time - begin_time))
            time.sleep(sleep_time)
        except Exception as e:
            logger.info(time.asctime())
            logger.info(e)
            # break
