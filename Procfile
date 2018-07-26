web: /usr/local/bin/uwsgi --chdir=/code/ --ini=/code/uwsgi.ini
worker: /usr/local/bin/celery -A knowhub worker -P gevent --uid 1
