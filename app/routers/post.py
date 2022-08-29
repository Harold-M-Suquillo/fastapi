from curses import curs_set
from unittest import result
from app import oauth2, schemas
from app.database import Database
from fastapi import status, HTTPException, APIRouter, Depends
from typing import List, Optional
from app import oauth2
from typing import Optional

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


# Retrieve all posts from table that the user has posted
@router.get('/', response_model=List[schemas.PostResponse])
def get_posts(current_user: dict = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    Database.cursor.execute(""" 
        SELECT * FROM posts 
        WHERE user_id=%s AND title LIKE %s
        ORDER BY created_at DESC
        LIMIT %s
        OFFSET %s; """,
        (current_user["id"], '%'+search+'%', limit, skip)
    )
    posts = Database.cursor.fetchall()

    Database.cursor.execute("""
        SELECT posts.post_id, COUNT(votes.post_id) 
        AS likes 
        FROM posts LEFT JOIN votes on posts.post_id = votes.post_id 
        GROUP BY posts.post_id; """)
    result = Database.cursor.fetchall()
    print(result)
    return posts





# Create a new post - Add the request maker as the owner
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, current_user: dict = Depends(oauth2.get_current_user)):
    Database.cursor.execute(""" INSERT INTO posts(title, content, published, user_id) VALUES(%s, %s, %s, %s) RETURNING *; """, 
                           (post.title, post.content, post.published, current_user["id"]))
    posts = Database.cursor.fetchone()
    Database.conn.commit()
    return posts





# Get an individual post by IDs
@router.get('/{id}', response_model=schemas.PostResponse)
def get_post(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    Database.cursor.execute(""" SELECT * FROM posts WHERE post_id=%s; """, (id,))
    post = Database.cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id [{id}] was not found")
    return post



# Delete a post based on id -> return nothing on success
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: dict = Depends(oauth2.get_current_user)):
    # try to find the post
    Database.cursor.execute(""" SELECT * FROM posts WHERE post_id=%s; """, (id,))
    found_post = Database.cursor.fetchone()

    # could not find post
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id [{id}] was not found")

    # Check if user is authorized to delete post
    if found_post['user_id'] == current_user['id']:
        Database.cursor.execute(""" DELETE FROM posts WHERE post_id=%s; """, (id,))
        Database.conn.commit()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action")


# Update a Post based on id -> updated post
@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, current_user: dict = Depends(oauth2.get_current_user)):

    # try to find the post
    Database.cursor.execute(""" SELECT * FROM posts WHERE post_id=%s; """, (id,))
    found_post = Database.cursor.fetchone()

    # could not find post
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id [{id}] was not found")

    # Check if user is authorized to modify post
    if found_post['user_id'] == current_user['id']:
        Database.cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE post_id=%s RETURNING *; """,
            (post.title, post.content, post.published, id))
        updated_post = Database.cursor.fetchone()
        Database.conn.commit()
        return updated_post
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action")
    

