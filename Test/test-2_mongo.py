import requests
import time
import threading
import json
import random
from pymongo import MongoClient

def test(n):
    print(n, 'begin')
    time.sleep(random.randint(1, 5))
    print(n, 'end')

    
def get_url(uid, p):
    url_template_1 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=100505%s"
    url_template_2 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s"
    url_template_3 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s&page=%d"

    url_template_4 = "https://m.weibo.cn/statuses/show?id=4293585023439336"
    url_template_5 = "https://m.weibo.cn/statuses/extend?id=4293695488100824"
    url_template_6 = "https://m.weibo.cn/api/statuses/repostTimeline?id=4293695488100824&page=2399"
    
    if p == 0:
        url = url_template_1 % (uid, uid)
    elif p == 1:
        url = url_template_2 % (uid, uid)
    else:
        url = url_template_3 % (uid, uid, p)

    return url


def run_with_threads(func, tasks, number_of_threads = 100):
    ts = list()
    while tasks or ts:
        while tasks and len(ts) < number_of_threads:
            task = tasks.pop()
            t = threading.Thread(target=func, args=task)
            t.start()
            ts.append(t)

        time.sleep(2)

        for t in reversed(ts):
            if not t.is_alive():
                ts.remove(t)

if __name__ == '__main__':

    uid = '2214838982'

# def carwl_uid(uid)
    # deal with single uid
    proxies = {'https': 'http://10.168.103.145:3128'}
    url = get_url(uid, 0)

    while True:
        try:
            r = requests.get(url, proxies=proxies, timeout=10)
            r_d = json.loads(r.text)
            if r_d["ok"] == 1:
                data = r_d['data']
                
            # def handle_userinfo(data)
                # deal with response.text
                userInfo = data['userInfo']
                statuses_count_now = userInfo['statuses_count']

                # mongodb
                client = MongoClient()
                weibo = client.weibo
                users = weibo.users
                # 
                user = users.find_one()
                if user:
                    print(user)
                    input('press to continue')
                    pass
                else:
                    mblog_num_to_crawl = statuses_count_now

                page_num_to_crawl = int((mblog_num_to_crawl + 3)/10) + 1
                tasks = [i for i in range(1, page_num_to_crawl+1)]

                # uid
                page = tasks[0]
            
            # def crawl_page(uid, page)
                #
                url = get_url(uid, page)
                # print(url)
                while True:
                    try:
                        r = requests.get(url, proxies=proxies, timeout=10)
                        response = json.loads(r.text)
                        if response['ok'] == 1:
                            data = response['data']
                            cards = data['cards']

                            # for card in cards:
                            card = cards[3]

                        # def handle_card
                            if card['card_type'] == 9:
                                mblog = card['mblog']

                                # to handle mblog content
                                pass
                                
                                # mongodb
                                client = MongoClient()
                                weibo = client.weibo
                                mblogs = weibo.mblogs
                                # 
                                mblogs_find = mblogs.find({'mid': mblog['mid']})
                                if mblogs_find.count():
                                    for i, mblog_find in enumerate(mblogs_find): 
                                        if i == 0:
                                            # update mblog
                                            print('to update mblog')
                                            pass
                                        else:
                                            # delete by "_id"
                                            mblogs.remove({'_id': mblog_find['_id']})
                                else:
                                    post_id = mblogs.insert_one(mblog).inserted_id
                                    print("post id is ", post_id)
                            else:
                                print(card['card_type'])
                            
                            
                        else:
                            print('page return {"ok": 0}')
                            input('press to continue')
                        
                        break
                    except Exception as e:
                        print('crawl_page', uid, page, e)
            
            
                break
            else:
                print('userInfo return {"ok": 0}')
                input('press to continue')
        except Exception as e:
            print('carwl_uid', uid, e)


    

    
