import os
from celery import Celery
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SQS_QUEUE = os.environ.get("SQS_QUEUE_NAME", "carbon-jobs")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")

celery = Celery("carbon", broker="sqs://")

celery.conf.update(
task_default_queue=SQS_QUEUE,
broker_transport_options={
"region": AWS_REGION,
"visibility_timeout": 60,
"predefined_queues": {
SQS_QUEUE: {"url": SQS_QUEUE_URL} if SQS_QUEUE_URL else {}
        },
    },
)