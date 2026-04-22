from fastapi import APIRouter,HTTPException,status,Depends
from .. import models
from ..database import get_db
from sqlalchemy.orm import Session
from .. import utils
from .. import oauth2
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix='/login',
    tags=['Authentication']
)

@router.post('/')
def login(user_creds : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_creds.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f'Invalid user credentials')
    
    if not utils.verify(user_creds.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials")
    
    access_token = oauth2.create_access_token(data={"user_id" : user.id})

    return {"access_token" : access_token, "token_type" : "Bearer"}