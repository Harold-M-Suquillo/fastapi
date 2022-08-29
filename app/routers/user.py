from app import schemas, utils
from app.database import Database
from app.constants import UNIQUE_VIOLATION
from fastapi import status, HTTPException, APIRouter

router = APIRouter(
    prefix='/users',
    tags=['users']
)


# Create a new user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse)
def create_post(user: schemas.UserCreate):
    try:
        hashed_password = utils.hash(user.password)
        Database.cursor.execute(""" INSERT INTO users(email, password) VALUES(%s, %s) RETURNING *; """, (user.email, hashed_password))
        new_user = Database.cursor.fetchone()
        Database.conn.commit()
        return new_user
    except UNIQUE_VIOLATION:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail=f"email [{user.email}] is already linked to an account")



















# get user info by id
@router.get('/{id}', response_model=schemas.UserDataResponse)
def find_user(id: int):
    Database.cursor.execute(""" SELECT * FROM users WHERE id=%s ; """, (id,))
    post = Database.cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id [{id}] was not found")
    return post
