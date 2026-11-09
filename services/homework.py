from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from common import db, INSTANCE, publish
import requests, json, uuid

app = FastAPI(title='Homework Service')
class HomeworkIn(BaseModel):
    user_id: str
    subject: str
    description: str
    deadline: str

@app.get('/health')
def health(): return {'status':'ok','service':'homework','instance':INSTANCE}

@app.post('/homeworks',status_code=201)
def create_homework(item: HomeworkIn):
    try:
        response=requests.get(f'http://users:8000/users/{item.user_id}',timeout=4)
        if response.status_code==404: raise HTTPException(400,'Unknown user')
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(503,'User Service unavailable') from exc
    task={'id':str(uuid.uuid4()),**item.model_dump(),'status':'new'}
    db().set('homework:'+task['id'],json.dumps(task))
    publish('homework.created',task)
    return {**task,'served_by':INSTANCE, 'sync_user_checked':True, 'event_published':True}

@app.get('/homeworks')
def list_homeworks():
    r=db(); keys=r.keys('homework:*')
    return {'items':[json.loads(value) for value in r.mget(keys) if value] if keys else [], 'served_by':INSTANCE}

@app.get('/homeworks/{task_id}')
def get_homework(task_id:str):
    raw=db().get('homework:'+task_id)
    if not raw: raise HTTPException(404,'Homework not found')
    return {**json.loads(raw),'served_by':INSTANCE}

@app.patch('/homeworks/{task_id}/complete')
def complete_homework(task_id:str):
    r=db(); raw=r.get('homework:'+task_id)
    if not raw: raise HTTPException(404,'Homework not found')
    task=json.loads(raw)
    if task['status']!='completed':
        task['status']='completed';r.set('homework:'+task_id,json.dumps(task));publish('homework.completed',task)
    return {**task,'served_by':INSTANCE,'event_published':True}
