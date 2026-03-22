""""
    This is a config file for celery worker which is being imported by the celery app

"""

broker_url = "redis://127.0.0.1:6379/0",
result_backend = "redis://127.0.0.1:6379/1"


task_serializer = "json"
result_serializer = "json"
accept_content = ['json']

timezone = "Asia/Kolkata"
enable_utc = False

worker_concurrency = 4
task_acts_late = True
task_reject_on_worker_lost = True