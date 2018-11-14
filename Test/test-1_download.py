import requests
import time
import threading
import json


def check(n):
    # proxies = {'https': 'http://127.0.0.1:3128'}
    proxies = {'https': 'http://10.168.103.145:3128'}
    for i in range(n):
        bt = time.time()
        try:
            r = requests.get('https://httpbin.org/ip', proxies=proxies)
        except Exception as e:
            print(e, '\n')
            continue
        et = time.time()

        print(round(et-bt, 5), r.text)

def m_check():
    ts = []
    for i in range(100):
        t = threading.Thread(target=check, args=(100,))
        t.start()
        ts.append(t)

def get_url(uid, p):
    url_template_1 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=100505%s"
    url_template_2 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s"
    url_template_3 = "https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s&page=%d"
    
    if p == 0:
        url = url_template_1 % (uid, uid)
    elif p == 1:
        url = url_template_2 % (uid, uid)
    else:
        url = url_template_3 % (uid, uid, p)

    return url
    
        

def download_with_uid(uid):
    return_flag = False
    page = 1
    while True:
        url = get_url(uid, page)
        proxies = {'https': 'http://10.168.103.145:3128'}
        while True:
            try:
                r = requests.get(url, proxies=proxies, timeout=10)
                return_flag = not deal_c(r.text)
                break
            except Exception as e:
                print(uid, page, e)
        if return_flag:
            break
        page += 1

def run(uids, number_of_threads = 100):
    ts = list()
    while uids or ts:
        while uids and len(ts) < number_of_threads:
            uid = uids.pop()
            t = threading.Thread(target=download_with_uid, args=(uid,))
            t.start()
            ts.append(t)
            
        time.sleep(5)

        for t in reversed(ts):
            if not t.is_alive():
                ts.remove(t)

def deal_c(text):
    d = json.loads(text)
    if d['ok'] == 0:
        return False

    data = d['data']
    for card in data['cards']:
        if card['card_type'] == 9:
            mblog = card['mblog']

            d = dict()
            print(mblog['created_at'],
                  mblog['mid'])
    return True


if __name__ == '__main__':

    uids = list()
    with open('uids_1000.txt', 'r') as f:
        for i in range(100):
            uid = f.readline().split()[0]
            uids.append(uid)

    proxies = {'https': 'http://10.168.103.145:3128'}
    url = get_url(uids[0], 1)

    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1750428112&containerid=1076031750428112'
    # r = requests.get(url, proxies=proxies)
    

    download_with_uid(uids[0])
        
    
        
    
        
