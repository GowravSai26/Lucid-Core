from rq import Worker, Queue
from Backend.utils.redis_connection import get_redis_connection

def start_worker():
    """
    Launches the background worker that listens to Redis queue 'lucid_queue'
    and executes any enqueued jobs asynchronously.
    """
    redis_conn = get_redis_connection()
    queue = Queue("lucid_queue", connection=redis_conn)
    
    print("🚀 Lucid Worker started.")
    print("📡 Connected to Redis at:", redis_conn)
    print("🧠 Listening to queue: lucid_queue")
    print("--------------------------------------------------")

    worker = Worker(queues=[queue], connection=redis_conn)
    worker.work(with_scheduler=True)

if __name__ == "__main__":
    start_worker()
