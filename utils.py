from settings import *
from mongoctl import MongoCtl
import requests
import json
import time
import random
import threading
import logging

mongoctl = MongoCtl()
logger_analyze = logging.getLogger('main.analyze')
logger = logging.getLogger('main.utils')


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
            with requests.get(url, proxies=proxies, timeout=timeout) as r:
                r_d = json.loads(r.text)
            if r_d['ok'] == 0:
                # log
                if r_d['msg'] == "\u8fd9\u91cc\u8fd8\u6ca1\u6709\u5185\u5bb9":  # 这里还没有内容
                    pass
                elif r_d['msg'] == "\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41,\u6b47\u6b47\u5427":   # 请求过于频繁,歇歇吧
                    if r_d['errno'] == "100005":
                        pass
                    else:
                        logger.debug(r.text)
                elif r_d['msg'] == "\u670d\u52a1\u5668\u8d70\u4e22\u4e86":      # 服务器走丢了
                    if r_d['errno'] == "100001":
                        pass
                    else:
                        logger.debug(r.text)
                else:
                    logger.debug(r.text)
                pass
            return r_d
        except Exception as e:
            if isinstance(e, json.decoder.JSONDecodeError):
                return {'ok': -2, 'failure_reason': 'server error: url cannot be found.'}
            elif isinstance(e, requests.exceptions.ProxyError):
                pass
            elif isinstance(e, requests.exceptions.SSLError):
                pass
            elif isinstance(e, requests.exceptions.ReadTimeout):
                pass
            elif isinstance(e, requests.exceptions.ConnectionError):
                pass
            elif isinstance(e, requests.exceptions.ChunkedEncodingError):
                pass
            elif isinstance(e, TypeError):
                logger.debug('TypeError:\n%s\n%s\n%s', r.text, url, type(r_d['msg']), exc_info=True)
            else:
                logger_analyze.debug('in get_dict_with_url: %s', type(e), exc_info=True)
                # print(type(e), e)
    # print('can not get {}'.format(url))
    return {'ok': -1, 'failure_reason': 'proxy error: the maximum number of retry is reached.'}


def get_mblog_url(mid):
    return mblog_url_template % mid


def get_user_url(uid):
    return user_url_template % (uid, uid)


def update_user_data_and_mids_queue(uid):
    if not mongoctl.change_uid_status(uid, STATUS_PROCESSING, former_status=STATUS_OUTSTANDING):
        if not mongoctl.change_uid_status(uid, STATUS_PROCESSING, former_status=STATUS_NEW_ADDED):
            return
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
            run_with_threads(add_mids_to_workqueue, urls, max_thread_num_for_mids_add)

            # update user data
            mongoctl.update_user_data(data)
        mongoctl.reset_uid_failures(uid)
        mongoctl.change_uid_status(uid, STATUS_OUTSTANDING, former_status=STATUS_PROCESSING, updated=True)
        return
    elif r_d['ok'] in (-2, 0):
        mongoctl.inc_uid_failures(uid)
        pass
    elif r_d['ok'] == -1:
        # print('read ok = -1', url)
        pass
    mongoctl.change_uid_status(uid, STATUS_OUTSTANDING, former_status=STATUS_PROCESSING)
    # print('{} update finish'.format(uid))


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
        if r_d['ok'] in (-2, -1, 0):
            return mids
        for card in r_d['data']['cards']:
            if card['card_type'] == 9:
                mids.append(card['mblog']['mid'])
    else:
        logger.info('get fail')
    return mids


def add_mids_to_workqueue(url):
    mids = get_mids_with_url(url)
    for mid in mids:
        # add mid to mongo
        mongoctl.add_new_mid(mid)


def add_uids_to_workqueue(uids):
    for uid in uids:
        # add uid to mongo
        mongoctl.add_new_uid(uid)


def get_mblog_by_mid(mid):
    if not mongoctl.change_mid_status(mid, STATUS_PROCESSING, STATUS_OUTSTANDING):
        return

    url = get_mblog_url(mid)
    r_d = get_dict_with_url(url)
    if r_d is None:
        status = STATUS_ERROR
    elif r_d['ok'] == -2 or r_d['ok'] == 0:
        status = STATUS_ERROR
    elif r_d['ok'] == -1:
        status = STATUS_OUTSTANDING
    else:
        status = STATUS_COMPLETE
        data = r_d['data']
        # update_user_data
        try:
            mongoctl.update_mblog_data(data)
        except Exception as e:
            logger_analyze.debug('in get_mblog_by_mid: %s', type(e), exc_info=True)

    mongoctl.change_mid_status(mid, status)


def mblogs_crawl(n=10000, thread_num=max_thread_num_for_mblogs_crawl):
    mids = mongoctl.get_mids_to_crawl(n)
    run_with_threads(get_mblog_by_mid, mids, thread_num)


def mids_crawl(n=10000, status=STATUS_OUTSTANDING, thread_num=max_thread_num_for_mids_crawl):
    uids = mongoctl.get_uids_to_crawl(n, status)
    run_with_threads(update_user_data_and_mids_queue, uids, thread_num)


def get_outstanding_mids_num():
    return mongoctl.get_mids_num(STATUS_OUTSTANDING)


def get_outstanding_uids_num():
    return mongoctl.get_uids_num(STATUS_OUTSTANDING)


#
def add_timestamp_for_mblogs(n=10000, max_times=0):
    mongoctl.add_timestamp_for_mblogs(n, max_times)


def check_proxies():
    for i in range(10):
        r = requests.get('https://httpbin.org/ip', proxies=proxies)
        print(r.text)


if __name__ == '__main__':
    # uid = '2214838982'
    uid = '5044281310'
    mid = '4270446973039872'

    uids = list()
    with open('Test/uids_1000.txt', 'r') as f:
        for line in f:
            uids.append(line.strip())

    # mid = '4303777261721996'
    url = get_mblog_url(mid)
    print(url)

    # r_d = get_dict_with_url(url)
    # print(r_d)

    # check_proxies()

    print(get_outstanding_mids_num())
    print(get_outstanding_uids_num())

    # update_user_data_and_mids_queue(uid)





