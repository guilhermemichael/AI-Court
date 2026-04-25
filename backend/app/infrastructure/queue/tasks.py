from app.infrastructure.queue.celery_app import celery_app


@celery_app.task(name="ai_court.health.ping")
def ping() -> str:
    return "pong"
