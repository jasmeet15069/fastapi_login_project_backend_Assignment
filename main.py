from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from pydantic import BaseModel
from database import SessionLocal, engine
from models import User
from auth import create_access_token
import asyncio

app = FastAPI()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == user.username))
        user_db = result.scalar_one_or_none()

    if user_db is None or not pwd_context.verify(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    asyncio.run(uvicorn.run(app, host="127.0.0.1", port=8000))
