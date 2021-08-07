pytrackdat django-manage collectstatic
pytrackdat django-manage migrate
gunicorn -u ptd_user -b :8000 -w 2 pytrackdat.ptd_site.ptd_site.wsgi:application
