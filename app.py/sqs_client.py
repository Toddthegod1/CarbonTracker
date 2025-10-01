import os
import boto3

_queue_url = os.environ.get("SQS_QUEUE_URL")
_region = os.environ.get("AWS_REGION", "us-east-1")

_sqs = boto3.client("sqs", region_name=_region)


def publish_recalc(user_id: int):
    """
    Publish a recalculation request to the SQS queue.
    """
    if not _queue_url:
        raise RuntimeError("SQS_QUEUE_URL not configured")

    _sqs.send_message(
        QueueUrl=_queue_url,
        MessageBody="recalc",
        MessageAttributes={
            "user_id": {"DataType": "Number", "StringValue": str(user_id)}
        },
    )