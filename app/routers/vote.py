from fastapi import status, HTTPException, APIRouter, Depends
from app import oauth2, schemas
from app.database import Database

router = APIRouter(
    prefix='/vote',
    tags=['Vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: dict = Depends(oauth2.get_current_user)):

    # Check if the post exists
    Database.cursor.execute(""" SELECT * FROM posts WHERE post_id=%s; """, (vote.post_id,));
    post = Database.cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id [{vote.post_id}]does not exist")

    # Query for post first -> If the post exists, the user has already liked the post
    Database.cursor.execute(""" SELECT * FROM votes WHERE post_id=%s AND user_id=%s; """, (vote.post_id, current_user["id"]));
    fetched_vote = Database.cursor.fetchone()
    if vote.dir:
        # User hasa already voted
        if fetched_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"user [{current_user['id']}] has already voted on post")
        # user has not voted
        Database.cursor.execute(""" INSERT INTO votes(post_id, user_id) VALUES (%s, %s); """, (vote.post_id, current_user["id"]))
        Database.conn.commit()
        return {"message": "succesfully added"}
    else:
        if not fetched_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"The vote does not exist")
        Database.cursor.execute(""" DELETE FROM votes WHERE post_id=%s AND user_id=%s;""", (vote.post_id, current_user["id"]))
        Database.conn.commit()
        return {"message": "succesfully deleted vote"}

