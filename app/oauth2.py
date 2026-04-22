from jose import JWTError,jwt
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from . import schemas
from sqlalchemy.orm import Session
from . import database,models
from .config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
#Generating a SECRET KEY  : 
# import secrets
# print(secrets.token_hex(32))


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data : dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token : str, creds_expection):
    try : 
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)

        id = payload.get("user_id")

        if not id: 
            raise creds_expection

        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise creds_expection

    return token_data

def get_current_user(token : str = Depends(oauth2_scheme),db : Session = Depends(database.get_db)):
    creds_expection = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not find the user creds",headers={"WWW-Authentication" : "Bearer"})

    token = verify_access_token(token,creds_expection)

    user =  db.query(models.User).filter(models.User.id == token.id).first()

    return user


