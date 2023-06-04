FROM python:3.9-alpine

RUN apk update && \
    apk add wget git && \
    git clone https://github.com/WilliamNing316/djangoForum.git && \
    pip install -r requirements.txt