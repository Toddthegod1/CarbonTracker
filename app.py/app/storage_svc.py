# app/storage_svc.py
import os, json
from typing import List, Dict

RAW_BUCKET = os.environ.get("S3_BUCKET", "file:///var/lib/carbon-tracker")
REGION = os.environ.get("AWS_REGION", "us-east-1")

def _is_s3() -> bool:
    return RAW_BUCKET.startswith("s3://")

def _bucket_or_path():
    return RAW_BUCKET.split("://", 1)[1]

# ---------- Local filesystem backend ----------
import os
def _fs_path(*parts: str) -> str:
    base = _bucket_or_path()  # base dir like /var/lib/carbon-tracker
    return os.path.join(base, *map(str, parts))

def _fs_read_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _fs_write_text(path: str, data: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

# ---------- S3 backend ----------
_s3 = None
def _s3():
    global _s3
    if _s3 is None:
        import boto3
        _s3 = boto3.client("s3", region_name=REGION)
    return _s3

def _s3_key_entries(user_id: int) -> str:
    return f"users/{user_id}/entries.jsonl"

def _s3_key_summary(user_id: int, period: str) -> str:
    return f"summaries/{user_id}/{period}.json"

# ---------- Public API ----------
def append_entry(user_id: int, entry: Dict):
    """Append one entry (JSON line) for a user."""
    if _is_s3():
        b = _bucket_or_path()
        s3 = _s3()
        key = _s3_key_entries(user_id)
        try:
            obj = s3.get_object(Bucket=b, Key=key)
            body = obj["Body"].read().decode("utf-8")
        except Exception:
            body = ""
        body += json.dumps(entry) + "\n"
        s3.put_object(Bucket=b, Key=key, Body=body.encode("utf-8"))
    else:
        p = _fs_path("users", user_id, "entries.jsonl")
        existing = _fs_read_text(p)
        existing += json.dumps(entry) + "\n"
        _fs_write_text(p, existing)

def list_entries(user_id: int, limit: int = 100) -> List[Dict]:
    if _is_s3():
        b = _bucket_or_path()
        s3 = _s3()
        key = _s3_key_entries(user_id)
        try:
            obj = s3.get_object(Bucket=b, Key=key)
            lines = obj["Body"].read().decode("utf-8").strip().splitlines()
        except Exception:
            return []
    else:
        p = _fs_path("users", user_id, "entries.jsonl")
        txt = _fs_read_text(p)
        lines = txt.strip().splitlines() if txt else []
    recs = [json.loads(l) for l in lines if l.strip()]
    recs.sort(key=lambda r: r.get("occurred_at", ""), reverse=True)
    return recs[:limit]

def write_summaries(user_id: int, period: str, rows: List[Dict]):
    payload = json.dumps(rows).encode("utf-8")
    if _is_s3():
        b = _bucket_or_path()
        _s3().put_object(Bucket=b, Key=_s3_key_summary(user_id, period), Body=payload)
    else:
        p = _fs_path("summaries", user_id, f"{period}.json")
        _fs_write_text(p, payload.decode("utf-8"))

def read_summaries(user_id: int, period: str) -> List[Dict]:
    if _is_s3():
        b = _bucket_or_path()
        s3 = _s3()
        key = _s3_key_summary(user_id, period)
        try:
            obj = s3.get_object(Bucket=b, Key=key)
            return json.loads(obj["Body"].read().decode("utf-8"))
        except Exception:
            return []
    else:
        p = _fs_path("summaries", user_id, f"{period}.json")
        txt = _fs_read_text(p)
        return json.loads(txt) if txt else []