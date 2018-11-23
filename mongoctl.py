from settings import *
import pymongo
from pymongo import MongoClient
import time
import logging
import json


class MongoCtl:
    def __init__(self):
        self.client = MongoClient(MONGODB_IP, MONGODB_PORT)
        self.client.admin.authenticate(MONGODB_USER, MONGODB_PWD)
        self.weibo = self.client.weibo

        # queue
        self.uids = self.weibo.uids
        self.mids = self.weibo.mids

        # data
        self.users = self.weibo.users
        self.mblogs = self.weibo.mblogs

        # config
        self.config = self.weibo.config

        # log
        self.logger = logging.getLogger('main.mongoctl')
        self.logger_analyze = logging.getLogger('main.analyze')

    def get_user_statuses_count(self, uid):
        record = self.users.find_one({
            'userInfo.id': int(uid)
        })
        if record is None:
            statuses_count = -1
        # get statuses_count and return
        else:
            statuses_count = record['userInfo']['statuses_count']
        return statuses_count

    def update_user_data(self, data):
        # uid = data['userInfo']['id']
        self.users.update({
                'userInfo.id': data['userInfo']['id']
            },
            data, upsert=True)

    def update_mblog_data(self, data):
        self.mblogs.update({
                'mid': data['mid']
            },
            data, upsert=True)

    def add_new_mid(self, mid):
        if self.mids.find_one({'mid': mid}):
            # print('mid {} has already existed.'.format(mid))
            return False
        else:
            data = {
                'mid': mid,
                'status': STATUS_OUTSTANDING,
                'update_time': time.time()
            }
            # self.mids.insert_one(data)
            self.mids.update(
                {'mid': mid},
                data,
                upsert=True
            )
            return True

    def add_new_uid(self, uid, status=STATUS_NEW_ADDED):
        if self.uids.find_one({'uid': int(uid)}):
            # print('uid {} has already existed.'.format(uid))
            return False
        else:
            data = {
                'uid': int(uid),
                'status': status,
                'updated': time.time(),
                'failures': 0
            }
            # self.uids.insert_one(data)
            self.uids.update(
                {'uid': int(uid)},
                data,
                upsert=True
            )
            return True

    def get_mid_to_crawl(self):
        data = self.mids.find_one_and_update(
            {'status': STATUS_OUTSTANDING}, {'$set': {'status': STATUS_PROCESSING}},
            sort=[('update_time', pymongo.DESCENDING)]
        )
        try:
            mid = data['mid']
        except Exception as e:
            mid = None
        return mid

    def get_mids_to_crawl(self, n=10000):
        mids = list()
        data = self.mids.find({'status': STATUS_OUTSTANDING}, sort=[('update_time', pymongo.DESCENDING)]).limit(n)
        for record in data:
            mids.append(record['mid'])
        return mids

    def get_uids_to_crawl(self, n=10000, status=STATUS_OUTSTANDING):
        # drop uids with max_continuous_failures_for_uid
        self.handle_uids_with_max_failures()

        uids = list()
        data = self.uids.find({'status': status}, sort=[('updated', pymongo.ASCENDING)]).limit(n)
        for record in data:
            uids.append(record['uid'])
        return uids

    def change_mid_status(self, mid, status, former_status=None):
        if former_status is None:
            data = self.mids.find_one_and_update(
                {'mid': mid}, {'$set': {'status': status}}
            )
        else:
            data = self.mids.find_one_and_update(
                {'mid': mid, 'status': former_status}, {'$set': {'status': status}}
            )
        if data is None:
            return False
        else:
            return True

    def change_uid_status(self, uid, status, former_status=None, updated=False):
        query_dict = {'uid': int(uid)}
        set_dict = {'status': status}
        if former_status is not None:
            query_dict['status'] = former_status
        if updated:
            set_dict['updated'] = time.time()
        data = self.uids.find_one_and_update(query_dict, {'$set': set_dict})
        if data is None:
            return False
        else:
            return True

    def get_mids_num(self, status=STATUS_OUTSTANDING):
        return self.mids.find({'status': status}).count()

    def handle_mids_with_status_processing_exception(self):
        data = self.mids.find({'status': 1})
        for record in data:
            mid = record['mid']
            rs = self.mids.find({'mid': mid})
            count = rs.count()
            if count == 1:
                print(count)
            elif count == 2:
                status = STATUS_PROCESSING
                for r in rs:
                    if r['status'] != STATUS_PROCESSING:
                        status = r['status']
                if status == STATUS_OUTSTANDING:
                    print(count, 'STATUS_OUTSTANDING')
                elif status == STATUS_COMPLETE:
                    mblog = self.mblogs.find_one({'mid': mid})
                    if mblog is None:
                        print(count, 'STATUS_COMPLETE', 'mid not in mblogs')
                    else:
                        self.mids.remove({'mid': mid, 'status': STATUS_PROCESSING})
                    pass
                elif status == STATUS_ERROR:
                    mblog = self.mblogs.find_one({'mid': mid})
                    if mblog is None:
                        self.mids.remove({'mid': mid, 'status': STATUS_PROCESSING})
                    else:
                        print(count, 'STATUS_ERROR', 'mid in mblogs')
                else:
                    print(count, 'STATUS_OTHERS')
            else:
                print(count)

    def handle_mids_with_status_error_exception(self, n=10000):
        # 1
        self.mids.update_many(
            {'status': STATUS_ERROR, 'retry': {'$exists': False}}, {'$set': {'retry': 0}}
        )
        # 2
        self.mids.remove({'status': STATUS_ERROR, 'retry': {'$gte': error_mid_max_retry_time}})
        # 3
        self.mids.update_many(
            {'status': STATUS_ERROR},
            {'$set': {'status': STATUS_OUTSTANDING}, '$inc': {'retry': 1}}
        )

    def inc_uid_failures(self, uid):
        self.uids.update(
            {'uid': int(uid)},
            {'$inc': {'failures': 1}}
        )

    def reset_uid_failures(self, uid):
        self.uids.update(
            {'uid': int(uid)},
            {'$set': {'failures': 0}}
        )

    def handle_uids_with_max_failures(self):
        self.uids.remove({'failures': {'$gte': max_continuous_failures_for_uid}})

    def get_config_mainloop(self):
        config = self.config.find_one()
        if config:
            if config['mainloop'] is True:
                return True
        return False

    def set_config_mainloop(self, mainloop=False):
        data = self.config.find_one()
        config_mainloop_set = {"mainloop": mainloop}
        if data is None:
            # init config
            self.config.insert(config_mainloop_set)
            pass
        else:
            self.config.update({}, {"$set": config_mainloop_set})


if __name__ == '__main__':
    mongoctl = MongoCtl()
    mid = '4298678506759937'
    former_status = STATUS_PROCESSING
    status = STATUS_OUTSTANDING

    # mongoctl.uids.update_many({}, {'$set': {'status': STATUS_NEW_ADDED}})
    mongoctl.handle_mids_with_status_processing_exception()





