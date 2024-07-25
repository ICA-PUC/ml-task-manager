"""Security Manager module"""
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.config import settings


class SecManager:
    """Security Manager class for all security related operations"""

    def __init__(self):
        envs = settings.env_confs
        self.secret = envs['SECRET_KEY']
        self.algorithm = envs['ALGORITHM']
        self.token_expire = envs['ACCESS_TOKEN_EXPIRE_MINUTES']
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict,
                            expires_delta: timedelta | None = None):
        """Create new access token using JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, self.secret,
                                algorithm=self.algorithm)
        return encode_jwt

    def verify_password(self, plain_password, hashed_password):
        """Verify password using passlib"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """Generate hash from given password string"""
        return self.pwd_context.hash(password)
