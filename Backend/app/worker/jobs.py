from redis import Redis
from rq import Queue
from ..config import settings
import os

redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn)

def enqueue_planner(db_dsn, project_id, goal_text):
    # simple enqueue; job function must be importable by RQ worker process
    # you can implement a wrapper that reconstitutes DB session and calls planner.generate_plan_sync
    job = q.enqueue("app.worker.job_functions.run_planner_job", db_dsn, project_id, goal_text)
    return job
