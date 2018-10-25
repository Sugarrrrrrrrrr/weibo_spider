import requests
import re
import lxml.etree
import json

if __name__ == '__main__':

    url = 'https://m.weibo.cn/detail/4253483656261491'
    r = requests.get(url)
    page = r.text

    s = r'''  render_data = \[*\]\[0\] \|\| {};'''
    s1 = r'render_data = \[([\s\S]*)\]\[0\] \|\| {};'

    pat = re.compile(s1)
    l = pat.findall(page)

    d = json.loads(l[0])
