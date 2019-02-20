FROM python:3.5 

MAINTAINER Sugar <zhangyushu@live.cn>

RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/sources.list

RUN apt-get update \
	&& rm /etc/localtime \
	&& ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
	&& mkdir /code

ENV PYTHONIOENCODING=utf-8

WORKDIR /code

RUN pip3 install pymongo requests pyyaml redis scrapy scrapy-redis -i https://pypi.tuna.tsinghua.edu.cn/simple/

CMD ["python3", "main.py"]

