from typing import Any, List, Annotated

from src.db.db import get_session
from src.config.settings import Config

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

oauth2_bearer = OAuth2PasswordBearer(tokenUrl=f"/{Config.VERSION}/auth/token")
db_dependency = Annotated[AsyncSession, Depends(get_session)]


