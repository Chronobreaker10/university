from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
import jwt
from datetime import datetime, timedelta, timezone
from core.config import settings
from core.schemas import TokenData
from core.errors import UnauthorizedError

password_hash = PasswordHash((
    Argon2Hasher(), BcryptHasher()
))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.security.expires_minutes * 60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


def validate_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError
        return TokenData(user_id=user_id)
    except jwt.InvalidTokenError as e:
        print(e.args)
        raise UnauthorizedError("Invalid token")
