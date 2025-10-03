import json
from app.api import app


app.testing = True
client = app.test_client()


def test_health():
    rv = client.get('/api/health')
    assert rv.status_code == 200


# Integration‑light test: add an entry; (recalc task requires worker)


def test_add_entry():
    payload = {"category":"electricity","quantity":10,"unit":"kWh"}
    rv = client.post('/api/entries', data=json.dumps(payload), headers={'Content-Type':'application/json','X-Demo-User':'1'})
    assert rv.status_code == 200
    assert rv.get_json().get('ok') is True