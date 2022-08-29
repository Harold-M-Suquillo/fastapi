from fastapi import APIRouter, status, HTTPException, Depends
from app.database import Database
from app import schemas, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas

router = APIRouter(
    tags=['Authentication']
)
# This dependency checks to see if the user passed a username and password as form data
@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):

    # Query database for user info
    Database.cursor.execute(""" SELECT * FROM users WHERE email=%s; """, (user_credentials.username,));
    fetched_data = Database.cursor.fetchone()

    # email not in database
    if not fetched_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")

    # Password not valid
    if not utils.verify(user_credentials.password, fetched_data['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid Credentials")
    print("We logged in")

    # Create and return access token
    access_token = oauth2.create_access_token(data= {"user_id": fetched_data['id']})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }





