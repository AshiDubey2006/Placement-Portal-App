from celery import Celery
from celery.schedules import crontab
from config import Config

def make_celery(app):
    """Create a Celery instance bound to a Flask app context."""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Standalone Celery instance used by tasks and workers
celery_app = Celery('placement_portal')
celery_app.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # -------------------------------------------------------
    # Beat schedule
    # -------------------------------------------------------
    beat_schedule={
        # Daily reminder at 08:00 UTC every day
        'daily-reminders': {
            'task': 'app.tasks.reminder_tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        # Monthly report on the 1st of every month at 07:00 UTC
        'monthly-report': {
            'task': 'app.tasks.report_tasks.send_monthly_report',
            'schedule': crontab(hour=7, minute=0, day_of_month=1),
        },
    },
    # Include task modules so beat can discover them
    include=[
        'app.tasks.reminder_tasks',
        'app.tasks.report_tasks',
        'app.tasks.export_tasks',
    ],
)
