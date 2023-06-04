FROM python:3.9-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories &&  \
    apk update && \
    apk add --no-cache wget git tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    git clone https://github.com/WilliamNing316/djangoForum.git && \
    pip install -r /djangoForum/requirements.txt

WORKDIR /djangoForum

EXPOSE 8000

ENTRYPOINT python manage.py runserver 0.0.0.0:8000
