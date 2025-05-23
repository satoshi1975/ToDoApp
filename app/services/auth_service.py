from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from app.core.config import settings
from app.db.models import User
from app.db.session import get_db, async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from sqlalchemy import select

bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, user: UserCreate) -> User:
        result = await self.session.execute(select(User).filter(User.username == user.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        hashed_password = await self.get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
    
    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
        user = await self._get_user_by_username(form_data.username)
        if not user or not await self.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await self._create_tokens(user)

    async def _create_tokens(self, user: User) -> Dict[str, str]:
        access_token = await self.create_access_token(data={"sub": user.username})
        refresh_token = await self.create_refresh_token(data={"sub": user.username})
        user.refresh_token = refresh_token
        await self.session.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    async def create_access_token(cls, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @classmethod
    async def get_current_user(cls, token: Optional[str] = Depends(oauth2_scheme)) -> User:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        async with async_session() as session:
            user = await cls._get_user_by_username(session, username)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user

    @classmethod
    async def _get_user_by_username(cls, session: AsyncSession, username: str) -> Optional[User]:
        result = await session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def verify_refresh_token(self, token: str) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._get_user_by_username(username)
        if not user or user.refresh_token != token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)