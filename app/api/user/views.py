from fastapi import APIRouter, Depends, HTTPException, status, Request
import jwt
from db.db import db_session
from api.user.schemas import UserSchema, APIKey, Signup, Login
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User
from api.user.authentication import token_generator, config_credentials, authorized_exception
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.user.services import UserService
from sqlalchemy import select
from db.models.api import ApiKey

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/signup')
async def create_user(user:Signup):
    user_service = UserService()
    new_user = user_service.create_user(user)
    new_user = User(**user.dict())
    return new_user

@router.post('/login')
async def login(form_data: Login):
    user_service = UserService()
    res = await user_service.token_generator(form_data.email, form_data.password)
    user, token = res['user'], res['access_token']
    try:
        payload = jwt.decode(token, config_credentials['SECRET_KEY'], config_credentials['ALGORITHM'])
    except:
        raise authorized_exception
    return  {
                'user': {
                    'id' : user.id,
                    'email' : user.email,
                    'first_name' : user.first_name,
                    'last_name' : user.last_name
                },
                'access_token' : token,'token_type' : 'bearer'
            }



@router.post("/get_api_key")
async def get_user_api_key(form_data : Login, session: AsyncSession = Depends(db_session)):
    try:
        user = await session.execute(
                select(User).where(email== form_data.email)
            )
    
        if user and await verify_password(password, user.password):
            key = session.query(ApiKey).get(user.id)
            if not key:
                key = APIKey(user=user.id)
                db.add(key)
                db.commit()
                db.refresh()
            user['api_key'] = key
            return user
    except:
        return {'detail': 'Invalid email or password'}

async def verify_api_key(request: Request, session: AsyncSession = Depends(db_session)):
    headers = request.headers
    if "Authorization" in headers:
        api_key = Request.headers
 
        try:
            verify_token = await session.execute(
                    select(ApiKey).where(key == api_key)
                )

            if verify_token:
                return {"api_key": True}
    
        except:
            raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="API Key not found"
                    )
            
    return {
        "Error": "Token is missing or incorrect header name"
        }, 401

@router.get("/protected", dependencies=[Depends(verify_api_key)])
def add_post() -> dict:
    return {
        "data": "You used a valid API key."
    }
    









# async def get_current_user(token : str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, config_credentials['SECRET_KEY'], config_credentials['ALGORITHM'])
#         user = await User.get(id=payload.get('id'))
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail = 'Invalid Username or Password',
#             headers={"WWW-Authenticate":'Bearer'}
#         )
#     return await user

# @router.post('/login')
# async def login(user: UserSchema = Depends(get_current_user)):
#     return {
#         'status' : 'ok',
#         'data' : {
#             'email' : user.email, 'first_name' :user.first_name, 'last_name' : user.last_name,
#             'is_verified' : user.is_verified
#         }
#     }


# @router.get("/my_details/")
# def get_current_user(current_user: User):
#     return current_user


# @router.get("/key")

# async def get_user_api_key():
#     # Check Database if User id exist
#     # Depends on session user id

#     # If user exist get user APIkey
#     userAPIKey = APIKey(
#         key="3fa85f64-5740-2262-b3fc-2c963f36afa1",
#         user="3fa85f64-5740-2262-b3fc-2c963f36afa1",
#     )

#     # Send key string
#     return userAPIKey
