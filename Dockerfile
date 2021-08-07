FROM pytrackdat_base_image:latest

ENV PYTHONUNBUFFERED 1

RUN mkdir /pytrackdat/
WORKDIR /pytrackdat/
ADD . /pytrackdat/

RUN set -ex \
    && python3 -m pip install --no-cache-dir .[gis] \
    && python3 -m pip install --no-cache-dir gunicorn==20.1.0 \
    && rm -rf /pytrackdat/pytrackdat

RUN useradd --home-dir /home/ptd_user --create-home ptd_user
WORKDIR /home/ptd_user
USER ptd_user

RUN mkdir -p /home/ptd_user/static  \
    && ln -s /usr/local/lib/python3.8/dist-packages/pytrackdat/ptd_site/databases /home/ptd_user/databases  \
    && ln -s /usr/local/lib/python3.8/dist-packages/pytrackdat/core/migrations /home/ptd_user/migrations

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=pytrackdat.ptd_site.ptd_site.settings
ENV DJANGO_ENV=production
ENV PTD_DESIGN_FILE=/home/ptd_user/design_file.csv
ENV PTD_STATIC_ROOT=/home/ptd_user/static
ENV PTD_GIS_MODE=True

CMD [ "bash", "/usr/local/lib/python3.8/dist-packages/pytrackdat/container_entry.bash" ]
