import uuid

from fastapi import UploadFile
from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, FileUrl, IPvAnyAddress, constr
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_extra_types.routing_number import ABARoutingNumber
from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber

from datetime import date, datetime
from typing import Optional, List, Annotated

from src.apps.accounts.enums import UserGender, UserMaritalStatus
from src.apps.portfolios.schemas import PortfolioRead
from src.apps.transactions.schemas import SubscriptionRead


class Message(BaseModel):
    message: str
    error_code: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    code: Optional[str]
    token_type: str = "bearer"
    user: "UserRead"
    valid_ip: bool
    message: str


class Verification(BaseModel):
    message: str
    code: str


class UserBaseSchema(BaseModel):
    firstName: Optional[Annotated[str, constr(max_length=255)]]  # First name with max length constraint
    lastName: Optional[Annotated[str, constr(max_length=255)]]  # Last name with max length constraint
    phoneNumber: Optional[Annotated[PhoneNumber, constr(min_length=10, max_length=14)]]  # Phone number with length constraints
    email: EmailStr  # Email with validation
    dob: Optional[datetime]
    gender: Optional[UserGender] = UserGender.OTHERS  # Assuming it's a string or replace with an Enum
    maritalStatus: Optional[UserMaritalStatus] = UserMaritalStatus.SINGLE  # Assuming it's a string or replace with an Enum

    class Config:
        from_attributes = True  # Allows loading from ORM models like SQLModel


class UserRead(UserBaseSchema):
    uid: uuid.UUID
    image: Optional[str] = None
    joined: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    isAdmin: bool = False
    isSuperuser: bool = False

    domains: List["KnownDomainsRead"] = []
    verifiedEmails: List["VerifiedEmailRead"] = []
    knownIps: List["KnownIpsRead"] = []
    verifiedDocuments: List["VerifiedDocumentRead"] = []
    subscription: Optional["SubscriptionRead"] = None
    bankAccount: Optional["BankAccountRead"] = None
    card: Optional["CardRead"] = None

    @property
    def age(self) -> Optional[int]:
        if self.dob:
            today = datetime.today().date()
            age = today.year - self.dob.year - (
                (today.month, today.day) < (self.dob.month, self.dob.day)
            )
            return age
        return 1


class UserCreateOrLoginSchema(BaseModel):
    email: EmailStr  # Email with validation
    password: Annotated[str, constr(max_length=8)]


class UserUpdateSchema(UserBaseSchema):
    password: Annotated[str, constr(max_length=8)]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str


class VerifiedEmailBase(BaseModel):
    email: EmailStr


class VerifiedEmailCreate(VerifiedEmailBase):
    pass


class VerifiedEmailRead(VerifiedEmailBase):
    uid: uuid.UUID
    verified_at: datetime
    domainUid: uuid.UUID
    userUid: uuid.UUID

    class Config:
        from_attributes = True


class KnownIpsRead(BaseModel):
    uid: uuid.UUID
    ip: IPvAnyAddress
    domainUid: uuid.UUID
    userUid: uuid.UUID

    class Config:
        from_attributes = True

class KnownDomainsRead(BaseModel):
    uid: uuid.UUID
    domain: AnyHttpUrl
    userUid: uuid.UUID

    verifiedEmails: List["VerifiedEmailRead"] = []
    knownIps: List["KnownIpsRead"] = []
    verifiedDocuments: List["VerifiedDocumentRead"] = []
    subscription: Optional["SubscriptionRead"] = None
    bankAccount: Optional["BankAccountRead"] = None
    card: Optional["CardRead"] = None

    class Config:
        from_attributes = True


class CreateOrUpdateVerifiedDocument(BaseModel):
    name: Annotated[str, constr(to_lower=True, strip_whitespace=True)]
    file: UploadFile

class VerifiedDocumentRead(BaseModel):
    uid: uuid.UUID
    name: Annotated[str, constr(to_lower=True, strip_whitespace=True)]
    file: FileUrl
    domainUid: uuid.UUID
    userUid: uuid.UUID
    approved: bool

    class Config:
        from_attributes = True


# Pydantic model for BankAccount
class BankAccountBase(BaseModel):
    bankName: Optional[Annotated[str, constr(max_length=255)]]
    accountNumber: Optional[Annotated[str, constr(max_length=20)]]
    sortCode: Optional[Annotated[str, constr(max_length=10)]]
    routingNumber: Optional[ABARoutingNumber]


class BankAccountRead(BankAccountBase):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    verified: bool = Field(default=False)
    domainUid: Optional[uuid.UUID]
    userUid: Optional[uuid.UUID]
    verified: bool = False

    class Config:
        from_attributes = True

class BankAccountCreateOrUpdate(BankAccountBase):
    pass


# Pydantic model for Card
class CardCreate(BaseModel):
    cardNumber: PaymentCardNumber
    expirationDate: date
    cvv: Annotated[str, constr(min_length=3, max_length=3)]


class CardUpdate(BaseModel):
    expirationDate: date
    cvv: Annotated[str, constr(min_length=3, max_length=3)]


class CardRead(BaseModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    valid: bool = Field(default=False)
    domainUid: Optional[uuid.UUID]
    userUid: Optional[uuid.UUID]

    class Config:
        from_attributes = True

    @property
    def cardBrand(self) -> PaymentCardBrand:
        return self.cardNumber.brand

    @property
    def expired(self) -> bool:
        return self.expirationDate < date.today()

