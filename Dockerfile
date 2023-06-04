FROM python:3.9-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories &&  \
    apk add --update --no-cache mariadb-connector-c-dev && \
    apk add --no-cache --virtual .build-deps wget git tzdata mariadb-dev mariadb-dev gcc g++ && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    git clone https://github.com/WilliamNing316/djangoForum.git && \
    pip install -r /djangoForum/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    apk del .build-deps

WORKDIR /djangoForum

EXPOSE 8000

ENTRYPOINT python manage.py runserver 0.0.0.0:8000
