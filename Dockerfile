FROM ubuntu

MAINTAINER Sugar <zhangyushu@live.cn>

RUN rm /etc/apt/sources.list
COPY sources.list /etc/apt/sources.list

RUN apt-get update \
	&& apt-get -y install python3 python3-pip tzdata \
	&& rm /etc/localtime \
	&& ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
	&& mkdir /code \
	&& pip3 install pymongo requests pyyaml

ENV PYTHONIOENCODING=utf-8

WORKDIR /code

CMD ["python3", "main.py"]

