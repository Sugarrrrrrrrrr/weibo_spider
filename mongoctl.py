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
            {'status': STATUS_OUTSTANDING}, {'$set': {'status': STATUS_PROCESSING}}, sort=[('_id', pymongo.DESCENDING)]
        )
        try:
            mid = data['mid']
        except Exception as e:
            mid = None
        return mid

    def get_mids_to_crawl(self, n=10000):
        mids = list()
        for i in range(n):
            mid = self.get_mid_to_crawl()
            if mid is None:
                break
            mids.append(mid)
        return mids

    def change_mid_status(self, mid, status):
        self.mids.find_one_and_update(
            {'mid': mid}, {'$set': {'status': status}}
        )


def test1():
    uid = '2214838983'
    mid = '4270446973039872'

    data = {
        'userInfo': {
            'id': 2214838983,
            'statuses_count': 7777,
            'time': 2
        }
    }

    mongoctl = MongoCtl()
    records = mongoctl.mids.find(sort=[('_id', pymongo.DESCENDING)]).limit(5)
    try:
        mongoctl.client.test.mids.insert(records)
    except Exception as e:
        if isinstance(e, pymongo.errors.DuplicateKeyError):
            print('already exist')
        else:
            print(e)

    def get_mid_to_crawl():
        data = mongoctl.client.test.mids.find_one_and_update(
            {'status': STATUS_OUTSTANDING}, {'$set': {'status': STATUS_PROCESSING}}, sort=[('_id', pymongo.DESCENDING)]
        )
        try:
            mid = data['mid']
        except Exception as e:
            mid = None
        return mid

    def get_mids_to_crawl(n=10):
        mids = list()
        for i in range(n):
            mid = get_mid_to_crawl()
            if mid is None:
                break
            mids.append(mid)
        return mids

    mids = get_mids_to_crawl()
    input(mids)

    status = STATUS_OUTSTANDING
    for mid in mids:
        mongoctl.client.test.mids.find_one_and_update(
            {'mid': mid}, {'$set': {'status': status}}
        )


if __name__ == '__main__':
    mongoctl = MongoCtl()
    data = mongoctl.mblogs.find_one()
    print(len(data['text']))
    print(data.keys())
    print(data['textLength'])