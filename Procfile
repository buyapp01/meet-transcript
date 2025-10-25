web: gunicorn attendee.wsgi
# Changed: Added --pool=solo to avoid prefork crash on Railway (48 workers causing OOM/crash loop)
# Previous: worker: celery -A attendee worker -l info
worker: celery -A attendee worker -l info --pool=solo