from celery import Celery
from kombu import Queue

REGION = "us-east-1"
ACCOUNT_ID = "330863234710"
QUEUE = "carbon-jobs"
CELERY_Q = "celery"  # broadcast/control queue

celery = Celery(__name__, broker="sqs://")

celery.conf.update(
    task_default_queue=QUEUE,
    task_default_routing_key=QUEUE,
    task_queues=(Queue(QUEUE, routing_key=QUEUE),),
    broker_transport_options={
        "region": REGION,
        "predefined_queues": {
            QUEUE:  {"url": f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/{QUEUE}"},
            CELERY_Q: {"url": f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/{CELERY_Q}"},
        },
        "visibility_timeout": 60,
        "polling_interval": 1,
    },
    worker_hijack_root_logger=False,
)