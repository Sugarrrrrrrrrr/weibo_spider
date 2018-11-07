from settings import *
import pymongo
from pymongo import MongoClient
import time
import json


class MongoCtl:
    def __init__(self):
        self.client = MongoClient()
        self.weibo = self.client.weibo

        # queue
        # self.uids = self.weibo.uids
        self.mids = self.weibo.mids

        # data
        self.users = self.weibo.users
        self.mblogs = self.weibo.mblogs

    def get_user_statuses_count(self, uid):
        record = self.users.find_one({
            'userInfo.id': int(uid)
        })
        if record is None:
            statuses_count = 0
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
            # print('{} has already existed.'.format(mid))
            pass
        else:
            data = {
                'mid': mid,
                'status': STATUS_OUTSTANDING,
                'update_time': time.time()
            }
            self.mids.insert_one(data)

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

    def get_mids_num(self, status=STATUS_OUTSTANDING):
        return self.mids.find({'status': status}).count()

    def handle_mids_with_status_processing_exception(self):
        self.mids.update_many(
            {'status': STATUS_PROCESSING}, {'$set': {'status': STATUS_OUTSTANDING}}
        )

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


if __name__ == '__main__':
    mongoctl = MongoCtl()
    mid = '4298678506759937'
    former_status = STATUS_PROCESSING
    status = STATUS_OUTSTANDING

    data = mongoctl.client.test.mids.find()
    print(data.count())

    # data = mongoctl.mids.find({'status': STATUS_ERROR}, sort=[('update_time', pymongo.DESCENDING)])
    # mongoctl.client.test.mids.insert(data)

    # data = mongoctl.client.test.mids.find({'status': STATUS_ERROR}, sort=[('update_time', pymongo.DESCENDING)])

    mongoctl.handle_mids_with_status_error_exception()
