from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from common import db, INSTANCE
import uuid

app = FastAPI(title="User Service")
class UserIn(BaseModel):
    name: str
    email: str

@app.get('/health')
def health(): return {'status':'ok','service':'users','instance':INSTANCE}

@app.post('/users', status_code=201)
def create_user(item: UserIn):
    user = {'id': str(uuid.uuid4()), 'name': item.name, 'email': item.email}
    db().set('user:'+user['id'], __import__('json').dumps(user))
    return {**user,'served_by':INSTANCE}

@app.get('/users/{user_id}')
def get_user(user_id: str):
    raw=db().get('user:'+user_id)
    if not raw: raise HTTPException(404, 'User not found')
    return {**__import__('json').loads(raw), 'served_by':INSTANCE}
