import os, json, boto3


_region = os.environ.get("AWS_REGION", "us-east-1")
_queue_url = os.environ.get("SQS_QUEUE_URL")


_sqs = boto3.client("sqs", region_name=_region)


def publish_recalc(user_id: int):
if not _queue_url:
# In local dev without SQS, skip silently for convenience
return
_sqs.send_message(QueueUrl=_queue_url, MessageBody=json.dumps({
"type": "recalc",
"user_id": user_id
}))