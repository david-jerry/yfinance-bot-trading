import random
import uuid

from datetime import datetime, timedelta
from typing import Annotated, Any, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# from src.app.auth.mails import send_card_pin, send_new_bank_account_details
from src.apps.accounts.schemas import BankAccountCreate, CreateOrUpdateVerifiedDocument, Token, UserCreateOrLoginSchema, UserUpdateSchema
from src.db.cloudinary import upload_image
from src.db.models import BankAccount, KnownDomains, KnownIps, User, VerifiedDocuments
from src.db.redis import store_allowed_ip, store_verification_code
from src.errors import BankAccountNotFound, InsufficientPermission, InvalidCredentials, UnknownIpConflict, UserAlreadyExists, UserNotFound
from src.utils.hashing import create_access_token, generate_verification_code, generateHashKey, verifyHashKey
from src.utils.logger import LOGGER
from src.config.settings import Config


class UserService:
    async def does_user_exist(self, email: Optional[str], uid: Optional[uuid.UUID], session: AsyncSession) -> User | None:
        if email is not None:
            db_result = await session.exec(select(User).where(User.email == email))
        else:
            db_result = await session.exec(select(User).where(User.uid == uid))

        user = db_result.first()
        return user

    async def does_ip_exist(self, user: User, ip: str, session: AsyncSession):
        db_result = await session.exec(select(KnownIps).where(KnownIps.userUid == user.uid).where(KnownIps.ip == ip))
        new_ip = db_result.first()
        if new_ip is None:
            return False
        return True

    async def does_domain_exist(self, user: User, domain: str, session: AsyncSession):
        db_result = await session.exec(select(KnownDomains).where(KnownDomains.userUid == user.uid).where(KnownDomains.domain == domain))
        new_ip = db_result.first()
        if new_ip is None:
            return False
        return True

    async def authenticate_user(self, form_data: UserCreateOrLoginSchema, ip: str, domain: str, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(email=form_data.email, session=session)

        if user is not None:
            valid_password = verifyHashKey(form_data.password, user.passwordHash)

            if valid_password:
                access_token = create_access_token(
                    user_data={
                        "email": user.email,
                        "user_uid": str(user.uid),
                    },
                    expiry=timedelta(seconds=Config.ACCESS_TOKEN_EXPIRY),
                )
                refresh_token = create_access_token(
                    user_data={
                        "email": user.email,
                        "user_uid": str(user.uid)
                    },
                    refresh=True,
                    expiry=timedelta(days=7),
                )
                code = None
                if not user.verifiedEmails:
                    code = generate_verification_code()
                    await store_verification_code(user.uid, code)

                approved = await self.does_domain_exist(user, domain, session)
                if not approved:
                    raise UserNotFound()

                # pass this with the response to send an email to the user
                valid_ip = await self.does_ip_exist(user, ip, session)
                return {
                        "message": "Authenticated successfully",
                        "code": code,
                        "user": user.model_dump_json(),
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "valid_ip": valid_ip,
                        "token_type": "bearer"
                    }
            else:
                raise InvalidCredentials()
        else:
            raise UserNotFound()

    async def register_new_user(self, permission: str, form_data: UserCreateOrLoginSchema, ip: str, domain: str, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(email=form_data.email, session=session)

        if user is not None:
            domain_exist = await self.does_domain_exist(user, domain, session)
            if domain_exist:
                raise UserAlreadyExists()
            else:
                new_domain = KnownDomains(domain=domain, user=user, userUid=user.uid)
                await session.add(new_domain)
                await session.commit()
                user.domains.append(new_domain)
                await session.commit()
                await session.refresh(user)

                code = None
                if not user.verifiedEmails:
                    code = generate_verification_code()
                    await store_verification_code(user.uid, code)

                return {
                    "message": "Account created successfully",
                    "code": code
                }


        data_dict = form_data.model_dump()
        new_user = User(**data_dict)
        new_user.passwordHash = generateHashKey(form_data.password)
        if permission == "admin":
            new_user.isAdmin = True
        elif permission == "superuser":
            new_user.isAdmin = True
            new_user.isSuperuser = True

        await session.add(new_user)
        await session.commit()

        new_ip = KnownIps(ip=ip, user=new_user, userUid=new_user.uid)
        await session.add(new_ip)
        await session.commit()

        new_domain = KnownDomains(domain=domain, user=new_user, userUid=new_user.uid)
        await session.add(new_domain)
        await session.commit()

        new_user.domains.append(new_domain)
        new_user.knownIps.append(new_ip)

        await session.commit()
        await session.refresh(new_user)

        code = generate_verification_code()
        await store_verification_code(new_user.uid, code)

        return {
            "message": "Account created successfully",
            "code": code
        }

    async def update_existing_user(self, user_uid: uuid.UUID, form_data: UserUpdateSchema, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        if form_data.password:
            user.passwordHash = generateHashKey(form_data.password)
        else:
            user_data = form_data.model_dump()
            for k, v in user_data.items():
                setattr(user, k, v)

        await session.commit()
        await session.refresh(user)
        return {
            "message": "Account updated successfully",
            "user": user
        }

    async def update_image(self, user_uid: uuid.UUID, image: UploadFile, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        user.image = await upload_image(image)

        await session.commit()
        await session.refresh(user)

    async def remove_user(self, user_uid: uuid.UUID, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        await session.delete(user)
        await session.commit()

    async def add_allowed_ip(self, user_uid: uuid.UUID, ip: str, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        new_ip = KnownIps(ip=ip, user=user, userUid=user.uid)
        await session.add(new_ip)
        await session.commit()

    async def add_verified_documents(self, form_data: List[CreateOrUpdateVerifiedDocument], user_uid: uuid.UUID, ip: str, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        # Process each item in form_data
        for document_data in form_data:
            # Convert each form_data item to a dictionary
            data_dict = document_data.model_dump()

            # Add user_uid to establish the relationship with the user
            data_dict["user_uid"] = user_uid
            data_dict["user"] = user

            # Create a new VerifiedDocuments object using the converted data
            new_document = VerifiedDocuments(**data_dict)

            # Add the new document to the session
            await session.add(new_document)
        await session.commit()

    async def update_verified_documents(self, user_uid: uuid.UUID, document_id: uuid.UUID, form_data: CreateOrUpdateVerifiedDocument, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        document_data = form_data.model_dump()
        for k, v in document_data.items():
            setattr(user, k, v)

        await session.commit()
        await session.refresh(user)
        return {
            "message": "Account updated successfully",
            "user": user
        }


    async def add_bank_account(self, form_data: BankAccountCreate, user_uid: uuid.UUID, ip: str, session: AsyncSession):
        user: Optional[User] = await self.does_user_exist(uid=user_uid, session=session)

        if user is None:
            raise UserNotFound()

        data_dict = form_data.model_dump()

        # Add user_uid to establish the relationship with the user
        data_dict["user_uid"] = user_uid
        data_dict["user"] = user

        # Create a new BankAccount object using the converted data
        new_bank = BankAccount(**data_dict)

        # Add the new document to the session
        await session.add(new_bank)
        await session.commit()
        return new_bank
