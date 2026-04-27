from pydantic import BaseModel,EmailStr
from pydantic.types import Literal
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title : str
    content : str
    published : bool = True


class CreatePost(PostBase):
    pass

class UpdatePost(PostBase):
    pass

class UserOut(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime

    model_config = {
        "from_attributes" : True
    }


class Post(PostBase):
    id : int
    createdAt : datetime
    user_id : int
    user : UserOut

    model_config = {
        "from_attributes" : True
    }

class PostOut(BaseModel):
    Post: Post
    votes : int
    model_config = {
        "from_attributes" : True
    }


class UserCreate(BaseModel):
    email : EmailStr
    password : str


class UserLogin(BaseModel):
    email :  EmailStr
    password : str

class Token(BaseModel):
    access_type : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[int] = None

class Vote(BaseModel):
    post_id : int
    vote_dir : Literal[0,1]