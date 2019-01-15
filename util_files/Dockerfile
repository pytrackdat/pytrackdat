FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED 1

ADD requirements.txt /requirements.txt
ADD install_dependencies.R /install_dependencies.R
# TODO: Is this needed:
ADD db.sqlite3 /db.sqlite3

RUN set -ex \
    && apk --update add --no-cache --virtual build-deps \
        autoconf automake gcc g++ make libc-dev bzip2-dev file musl-dev linux-headers pcre pcre-dev \
    && apk add --no-cache R R-dev \
    && pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache-dir -r /requirements.txt" \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache-dir uwsgi==2.0.17.1" \
    && chmod -R a+w /usr/lib/R/library \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "Rscript /install_dependencies.R" \
    && apk del build-deps
RUN mkdir /code/
WORKDIR /code/
ADD . /code/

EXPOSE 8000

ENV DJANGO_ENV=production
ENV UWSGI_WSGI_FILE=SITE_NAME/wsgi.py UWSGI_SOCKET=0.0.0.0:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8
ENV UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
