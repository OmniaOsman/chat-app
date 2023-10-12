from celery import Celery
app = Celery('chat', broker='redis')

app.config_from_object('celeryconfig', 
                       include=['CELERY_BROKER_URL', 
                                'CELERY_RESULT_BACKEND', 
                                'CELERY_TASK_ROUTES'])
