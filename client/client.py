from celery import Celery

# Connect to the Celery broker (Redis in Docker, mapped to host)
app = Celery(
    "client",
    broker="redis://127.0.0.1:6379/0",   # host machine access
    backend="redis://127.0.0.1:6379/1"   # optional, for task result
)

# Name of the task to trigger
task_name = "ml_engine.fake_detector.tasks.process_reviews"
# task_name = "ml_engine.sentiment_analysis.tasks.sentiment_analysis_func"
# task_name="celery_worker.worker.fake_detector_task"
# Send the task to the worker
result = app.send_task(task_name)

print(f"Task has been sent! Task ID: {result.id}")

# Optional: wait for result (if you configured backend)
# print("Result:", result.get(timeout=10))