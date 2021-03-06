

proxies = {'http': 'http://10.168.103.145:3128',
           'https': 'https://10.168.103.145:3128'}
max_retry_time = 10
error_mid_max_retry_time = 5
max_continuous_failures_for_uid = 10
timeout = 10
max_page_num = 50
max_thread_num_for_mblogs_crawl = 100
max_thread_num_for_mids_crawl = 100
max_thread_num_for_mids_add = 10

logging_config = 'logging_config.yaml'

mblog_url_template = 'https://m.weibo.cn/statuses/show?id=%s'
user_url_template = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=100505%s'
mblog_list_url_template = 'https://m.weibo.cn/api/container/getIndex?containerid=107603%s'
mblog_list_url_with_page_template = '&page=%d'

MONGODB_IP = '10.168.103.145'
MONGODB_PORT = 27017
MONGODB_USER = 'weibo'
MONGODB_PWD = '1q2w3e4r5t'

STATUS_OUTSTANDING = 0
STATUS_PROCESSING = 1
STATUS_COMPLETE = 2             # for mids
STATUS_ERROR = 3
STATUS_NEW_ADDED = 4            # for uids
