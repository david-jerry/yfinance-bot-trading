from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.db import get_session
from src.apps.accounts.schemas import Message, Token, UserCreateOrLoginSchema, Verification
from src.apps.accounts.services import UserService
from src.errors import InvalidCredentials, UserAlreadyExists, UserNotFound
from src.config.settings import Config
from src.db.redis import (
    get_password_reset_code,
    get_verification_status,
    store_password_reset_code,
    store_verification_code,
)
from src.utils.hashing import create_access_token, generate_verification_code, verifyHashKey

db_dependency = Annotated[AsyncSession, Depends(get_session)]
user_service = UserService()
auth_router = APIRouter()


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=Verification, responses={status.HTTP_404_NOT_FOUND: {"model": Message}})
async def register(permission: Optional[str], form_data: Annotated[UserCreateOrLoginSchema, Depends()], request: Request, db_dependency):
    domain = request.headers.get("Domain") or "http://localhost:3000"
    ip = request.headers.get("Ip") or "127.0.0.1"

    try:
        await user_service.register_new_user(permission, form_data, ip, domain, db_dependency)
    except UserAlreadyExists:
        raise JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User with this email already exists", "error_code": "user_already_exist"}
        )
    except Exception as e:
        raise JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Error Registering you: {str(e)}", "error_code": "registration_error"}
        )

@auth_router.post("/token", status_code=status.HTTP_200_OK, response_model=Token, responses={status.HTTP_404_NOT_FOUND: {"model": Message}})
async def login(form_data: Annotated[UserCreateOrLoginSchema, Depends()], request: Request, db_dependency):
    domain = request.headers.get("Domain") or "http://localhost:3000"
    ip = request.headers.get("Ip") or "127.0.0.1"
    try:
        await user_service.authenticate_user(form_data, ip, domain, db_dependency)
    except UserNotFound:
        raise JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found", "error_code": "user_not_found"}
        )
    except InvalidCredentials:
        raise JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Invalid email or password.", "error_code": "invalid_email_or_password"}
        )
