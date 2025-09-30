import os
from functools import wraps
from flask import request, jsonify
from models import ensure_demo_user


# Extremely simple demo auth


DEMO_USER_ID = int(os.environ.get("DEMO_USER_ID", "1"))




def require_user(fn):
@wraps(fn)
def wrapper(*args, **kwargs):
ensure_demo_user()
uid = request.headers.get("X-Demo-User")
try:
uid = int(uid) if uid else DEMO_USER_ID
except Exception:
return jsonify({"error": "invalid user"}), 400
user = {"id": uid, "email": f"demo{uid}@example.com"}
return fn(user, *args, **kwargs)
return wrapper