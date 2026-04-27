from fastapi import Response,status,HTTPException,Depends
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schemas
from .. import models
from fastapi import APIRouter
from .. import oauth2
from typing import List,Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# Creating get all posts api:
@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db : Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user),limit : int = 10,skip : int = 0,search : Optional[str]=""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.user_id==current_user.id).all()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# Creating api for getting one post :
@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id : int,db : Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id=%s""",(str(id)))
    # post = db.query(models.Post).filter(models.Post.id==id).first()
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"There is exists no post with id : {id}")
    
    return post


# Creating post :
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post : schemas.CreatePost,db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    new_post = models.Post(user_id = current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Creating api to delete post :
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int,db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""",(str(id)))
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="There exists no post with id : {id}")
    
    if post.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    
    db.delete(post)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#Creating api to update a post :
@router.put("/{id}",response_model=schemas.Post)
def update_post(updated_post : schemas.UpdatePost,id : int,db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title=%s,content=%s,published=%s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)))
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='There exists no such post with id : {id}')
    
    if post.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
    
    post_query.update(updated_post.model_dump(),synchronize_session=False)
    db.commit()
    return post_query.first()
