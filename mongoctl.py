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
            self.mids.insert_one(data)
            return True

    def add_new_uid(self, uid):
        if self.uids.find_one({'uid': int(uid)}):
            # print('uid {} has already existed.'.format(uid))
            return False
        else:
            data = {
                'uid': int(uid),
                'status': STATUS_OUTSTANDING,
                'updated': time.time(),
                'failures': 0
            }
            self.uids.insert_one(data)
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

    def get_uids_to_crawl(self, n=10000):
        # drop uids with max_continuous_failures_for_uid
        self.handle_uids_with_max_failures()

        uids = list()
        data = self.uids.find({'status': STATUS_OUTSTANDING}, sort=[('updated', pymongo.ASCENDING)]).limit(n)
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


if __name__ == '__main__':
    mongoctl = MongoCtl()
    mid = '4298678506759937'
    former_status = STATUS_PROCESSING
    status = STATUS_OUTSTANDING

    # data = mongoctl.client.test.mids.find()
    # print(data.count())

    # data = mongoctl.mids.find({'status': STATUS_ERROR}, sort=[('update_time', pymongo.DESCENDING)])
    # mongoctl.client.test.mids.insert(data)

    # data = mongoctl.client.test.mids.find({'status': STATUS_ERROR}, sort=[('update_time', pymongo.DESCENDING)])

    # mongoctl.handle_mids_with_status_error_exception()

    mongoctl.handle_mids_with_status_processing_exception()

    s1 = set()
    data = mongoctl.uids.find({'failures': 0})
    for record in data:
        s1.add(record['uid'])

    s2 = set()
    data = mongoctl.uids.find({'failures': 1})
    for record in data:
        s2.add(record['uid'])

    s3 = set()
    data = mongoctl.uids.find({'failures': 2})
    for record in data:
        s3.add(record['uid'])

    s4 = set()
    data = mongoctl.uids.find({'failures': 3})
    for record in data:
        s4.add(record['uid'])

    sx = set()
    data = mongoctl.users.find()
    for record in data:
        sx.add(record['userInfo']['id'])

    print(1, 'x', '____')
    for s in s1:
        if s not in sx:
            print(s)

    print(2, 'x', '____')
    for s in s2:
        if s in sx:
            print(s)

    print(3, 'x', '____')
    for s in s3:
        if s in sx:
            print(s)

    print(4, 'x', '____')
    for s in s4:
        if s in sx:
            print(s)
