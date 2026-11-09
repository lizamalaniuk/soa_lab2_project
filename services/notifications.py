from fastapi import FastAPI
from common import db, INSTANCE
import json

app=FastAPI(title='Notification Service')
@app.get('/health')
def health(): return {'status':'ok','service':'notifications','instance':INSTANCE}
@app.get('/notifications')
def notifications():
    raw=db().lrange('notifications',0,-1)
    return {'items':[json.loads(i) for i in raw], 'served_by':INSTANCE}
