

proxies = {'https': 'http://10.168.103.145:3128'}
max_retry_time = 10
timeout = 10
max_page_num = 50
max_thread_num_for_mblogs_crawl = 100

mblog_url_template = 'https://m.weibo.cn/statuses/show?id=%s'
user_url_template = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=100505%s'
mblog_list_url_template = 'https://m.weibo.cn/api/container/getIndex?containerid=107603%s'
mblog_list_url_with_page_template = '&page=%d'

STATUS_OUTSTANDING = 0
STATUS_PROCESSING = 1
STATUS_COMPLETE = 2
STATUS_ERROR = 3
