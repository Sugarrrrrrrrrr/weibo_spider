from settings import *
from mongoctl import MongoCtl
import requests
import json
import time
import random
import threading

mongoctl = MongoCtl()


def run_with_threads(func, tasks, number_of_threads=100):
    ts = list()
    while tasks or ts:
        while tasks and len(ts) < number_of_threads:
            task = tasks.pop()
            t = threading.Thread(target=func, args=(task,))
            t.start()
            ts.append(t)

        time.sleep(2)

        for t in reversed(ts):
            if not t.is_alive():
                ts.remove(t)


def get_dict_with_url(url, max_retry_time=max_retry_time):
    for i in range(max_retry_time):
        try:
            r = requests.get(url, proxies=proxies, timeout=timeout)
            r_d = json.loads(r.text)
            return r_d
        except Exception as e:
            pass
            # print(e)
    print('can not get {}'.format(url))
    return {'ok': 0, 'failure_reason': 'proxy error: the maximum number of retry is reached.'}


def get_mblog_url(mid):
    return mblog_url_template % mid


def get_user_url(uid):
    return user_url_template % (uid, uid)


def update_user_data_and_mids_queue(uid):
    url = get_user_url(uid)
    r_d = get_dict_with_url(url)
    if r_d['ok'] == 1:
        data = r_d['data']
        statuses_count_new = data['userInfo']['statuses_count']

        # get statuses_count_old from mongo
        statuses_count_old = mongoctl.get_user_statuses_count(uid)

        count = statuses_count_new - statuses_count_old
        if count > 0:
            urls = get_mblog_list_urls(uid, count)
            run_with_threads(add_mids_to_workqueue, urls, 10)

            # update user data
            mongoctl.update_user_data(data)
    print('{} update finish'.format(uid))


def get_mblog_list_url(uid, page=1):
    url = mblog_list_url_template % uid
    if page != 1:
        url += mblog_list_url_with_page_template % page
    return url


def get_mblog_list_urls(uid, count=0, max_page_num=max_page_num):
    page_num = int(count/10) + 1
    page_num = min([page_num, max_page_num])
    urls = [get_mblog_list_url(uid, page) for page in range(1, page_num+1)]
    return urls


def get_mids_with_url(url):
    r_d = get_dict_with_url(url)
    mids = list()
    if r_d is not None:
        if r_d['ok'] == 0:
            return mids
        for card in r_d['data']['cards']:
            if card['card_type'] == 9:
                mids.append(card['mblog']['mid'])
    else:
        print('get fail')
    return mids


def add_mids_to_workqueue(url):
    mids = get_mids_with_url(url)
    for mid in mids:
        # add mid to mongo
        mongoctl.add_new_mid(mid)


def get_mblog_by_mid(mid):
    url = get_mblog_url(mid)
    r_d = get_dict_with_url(url)

    if r_d is None:
        status = STATUS_ERROR
    elif r_d['ok'] == 0:
        status = STATUS_ERROR
    else:
        status = STATUS_COMPLETE
        data = r_d['data']
        # update_user_data
        mongoctl.update_mblog_data(data)

    mongoctl.change_mid_status(mid, status)


def mblogs_crawler(n=10000, thread_num=max_thread_num_for_mblogs_crawl):
    mids = mongoctl.get_mids_to_crawl(n)
    run_with_threads(get_mblog_by_mid, mids, thread_num)


if __name__ == '__main__':
    uid = '2214838982'
    mid = '4270446973039872'

    uids = list()
    with open('uids.txt', 'r') as f:
        for line in f:
            uids.append(line.strip())

    # run_with_threads(add_mids_to_workqueue, get_mblog_list_urls(uid, 1000))
    # update_user_data_and_mids_queue(uid)
    # run_with_threads(update_user_data_and_mids_queue, uids, 100)

    # mid = mongoctl.get_mid_to_crawl()
    # get_mblog_by_mid(mid)

    # mblogs_crawler
    mblogs_crawler(10000)




