web: newrelic-admin run-program gunicorn heroku_wsgi -b 0.0.0.0:$PORT -w 4
worker: src/manage.py listenfortweets
