from ..models import Vote
from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from .. import oauth2
from .. import models

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)


@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote : schemas.Vote, db : Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id==vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Post with id : {vote.post_id} does not exits')

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,models.Vote.user_id == current_user.id)

    found_vote = vote_query.first()

    if vote.vote_dir==1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'user {current_user.id} has already vote on post {vote.post_id}')
        
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message" : f"{current_user.id} has successfully vote to the post {vote.post_id}"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vote does not exist")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message" : "Successfully deleted post"}

