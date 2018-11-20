import mids_crawler
import mblogs_crawler
from utils import *
from logging_config import setup_logging
import time
import datetime

if __name__ == '__main__':

    setup_logging(logging_config)
    logger = logging.getLogger('main')

    # config
    data = mongoctl.config.find_one()
    if data is None:
        # init config
        mongoctl.config.insert({"mainloop": True})
        pass

    config_mainloop_set = {"mainloop": True}
    mongoctl.config.update({}, {"$set": config_mainloop_set})

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

            logger.info('mids_crawler.running ----------------------------------------')
            mids_crawler.run()
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

            end_time = datetime.datetime.now()
            logger.info('\ncost: %s\n##### sleeping #####\n\n' % str(end_time - begin_time))

            # begin stop check
            if not mongoctl.get_config_mainloop():
                break
            # finish stop check

            time.sleep(0.5 * 60 * 60)
        except Exception as e:
            logger.info(time.asctime())
            logger.info(e)
            # break
