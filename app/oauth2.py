from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from app import schemas
from fastapi.security import OAuth2PasswordBearer
from app.database import Database
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Environment variables
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Creates an token
def create_access_token(data: dict):
    # Create copy as we will modify data
    to_encode = data.copy();

    # Provide time for expiration 
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])     # Decode the JWT
        id: str = payload.get('user_id')                                   # get individual field from JWT payload

        if not id:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)   # This will validate it matches our schema, if extra properties we pass it here
    except JWTError:
        raise credentials_exception
    return token_data   # id -> in the future we may add to the payload and


# This depedncy looks the authorization header and checks if the user passed Bearer + token
def get_current_user(token: str = Depends(oauth2_scheme)):
    # credential exception 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Could not validate Credentials", headers={"WWW-Authenticate": "Bearer"})
    # Verify the toke
    token = verify_access_token(token, credentials_exception)

    # Get user data from Database
    Database.cursor.execute(""" SELECT * FROM users WHERE id=%s; """, (token.id,))
    fetched_user = Database.cursor.fetchone()
    return { "id": fetched_user["id"] }

