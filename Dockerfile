FROM osgeo/gdal:alpine-normal-3.2.2

ENV PYTHONUNBUFFERED 1

RUN mkdir /pytrackdat/
WORKDIR /pytrackdat/
ADD . /pytrackdat/

RUN set -ex \
    && apk add --no-cache --virtual build-deps \
        autoconf automake gcc g++ git make libc-dev libxml2-dev bzip2-dev file musl-dev linux-headers pcre pcre-dev \
        unzip \
    && apk add --no-cache python3 python3-dev R R-dev \
    && apk add libspatialite --repository http://nl.alpinelinux.org/alpine/edge/testing \
    && ln -s /usr/lib/mod_spatialite.so.7 /usr/lib/mod_spatialite.so \
    && pip3 install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip3 install --no-cache-dir .pytrackdat[gis]" \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip3 install --no-cache-dir uwsgi==2.0.19.1" \
    && chmod -R a+w /usr/lib/R/library \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "Rscript /pytrackdat/util_files/install_dependencies.R" \
    && apk del build-deps

RUN useradd --home-dir /home/ptd_user --create-home ptd_user
WORKDIR /home/ptd_user
USER ptd_user

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=pytrackdat.ptd_site.ptd_site.settings
ENV DJANGO_ENV=production
ENV UWSGI_WSGI_FILE=SITE_NAME/wsgi.py UWSGI_SOCKET=0.0.0.0:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8
ENV UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
