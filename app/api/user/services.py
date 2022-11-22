from  passlib.context import CryptContext
from api.user.schemas import UserSchema, APIKey, Signup, Login
from db.db import db_session
from db.models.user import User
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt

pwd_crypt = CryptContext(schemes=['bcrypt'], deprecated='auto')
config_credentials = {
    'SECRET_KEY' : "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    'ALGORITHM' : "HS256",
    'ACCESS_TOKEN_EXPIRE_MINUTES' : 30
}

authorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail = 'Invalid Email or Password',
    headers={"WWW-Authenticate":'Bearer'}
)

class UserService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session

    async def create_user(self, user: Signup) -> User:
        new_user = User(**user.dict())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return await new_user
    
    def get_hashed_password(self, password):
        return pwd_crypt.hash(password)


    async def verify_password(self, plain_password, hashed_password):
        return pwd_crypt.verify(plain_password, hashed_password)

    async def authenticate_user(self,email, password):
        statement = select(User).where(email==email)
        try:
            user = await self.session.execute(statement)
            if user and await self.verify_password(password, user.password):
                return user
        except:
            return False


    def create_access_token(data: dict, expires_delta: timedelta= None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config_credentials['SECRET_KEY'], algorithm=config_credentials['ALGORITHM'])
        return encoded_jwt
    
    async def token_generator(self, email : str, password : str):
        user = await self.authenticate_user(email, password)
        if not user:
            raise authorized_exception
        data = {
            'id' : f'{user.id}',
            'email' : user.email
        }
        access_token_expires = timedelta(minutes=config_credentials['ACCESS_TOKEN_EXPIRE_MINUTES'])
        access_token = self.create_access_token(
            data, expires_delta=access_token_expires
        )
        return {'user': user, 'access_token' : access_token}
    


