"""Security Manager module"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import jwt
from passlib.context import CryptContext
from app.config import settings


class SecManager:
    """Security Manager class for all security related operations"""

    def __init__(self):
        envs = settings.env_confs
        self.secret = envs['SECRET_KEY']
        self.algorithm = envs['ALGORITHM']
        self.token_expire = int(envs['ACCESS_TOKEN_EXPIRE_MINUTES'])
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.creds_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def create_access_token(self, data: dict,
                            expires_delta: timedelta | None = None):
        """Create new access token using JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret,
                                 algorithm=self.algorithm)
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        """Verify password using passlib"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """Generate hash from given password string"""
        return self.pwd_context.hash(password)

    def authenticate_user(self, dbm, username: str, password: str):
        """Check provided credentials against those saved in DB"""
        user = dbm.get_user_by_name(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
