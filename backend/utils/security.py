import logging
import os
import secrets
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configurare Hashing (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurare JWT
# The signing key comes from the SECRET_KEY environment variable (or a local .env file).
# Production (APP_ENV=production, or running on Render) refuses to start without it.
# Local dev without SECRET_KEY gets a random per-process key: tokens stop working on restart.
_IS_PRODUCTION = (
    os.getenv("APP_ENV", "").lower() in ("production", "prod")
    or os.getenv("RENDER", "").lower() == "true"
)

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    if _IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. Refusing to start in production "
            "without a JWT signing key. Generate one with: "
            "python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    SECRET_KEY = secrets.token_urlsafe(64)
    logger.warning(
        "SECRET_KEY is not set; using a random development key. "
        "Login tokens will be invalid after a restart. Set SECRET_KEY in backend/.env."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt