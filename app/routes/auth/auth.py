# app/routes/auth.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import User, UserIn
from app.db.database import db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import SECRET_KEY
from jose import jwt

router = APIRouter(prefix="", tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return User(**user)
    return None

@router.post("/register")
async def register(user_in: UserIn):
    # Check if user already exists.
    if await get_user(user_in.username):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create a user dictionary and store it in MongoDB.
    user_dict = {
        "username": user_in.username,
        "hashed_password": hash_password(user_in.password)
    }
    print("User dict from register route", user_dict)
    await db.users.insert_one(user_dict)
    return {"message": "User created successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/users/me")
async def get_user_me(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    return user
