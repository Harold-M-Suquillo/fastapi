from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import post, user, authentication, vote
from app.database import Database
from app.config import settings


# Create fastAPI instance
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://10.0.0.240:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to the database
@app.on_event("startup")
def startup_event():
    Database.connect(
        settings.database_hostname,
        settings.database_name,
        settings.database_username,
        settings.database_password
    )
    print("Database Connection opened")

# Close Database Connection
@app.on_event("shutdown")
async def shutdown_event():
    Database.disconnect()
    print("Database Connection closed")

@app.get("/")
async def root():
    return {"message": "HI FATTY"}

# Link all the API routes
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)
app.include_router(authentication.router)




 


