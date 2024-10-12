from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pydantic import AnyHttpUrl, EmailStr, FileUrl, IPvAnyAddress
from sqlmodel import SQLModel, Field, Relationship, Column
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import List, Optional
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_extra_types.routing_number import ABARoutingNumber
from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber

from src.apps.accounts.enums import UserGender, UserMaritalStatus
from src.apps.transactions.enums import TransactionPaymentMethod, TransactionPaymentType, TransactionStatus

# User Specific Models
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[PhoneNumber] = Field(nullable=True, max_length=16, unique=True)
    email: EmailStr = Field(nullable=False, unique=True, index=True, max_length=255)
    dob: Optional[datetime] = Field(
        default_factory=None,
        sa_column=Column(pg.TIMESTAMP, nullable=True, default=None),
    )
    image: Optional[str] = Field(default=None)
    passwordHash: str = Field(nullable=False)  # Store hashed passwords

    gender: Optional[UserGender]
    maritalStatus: Optional[UserMaritalStatus]


    # Dates
    joined: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )

    # Permissions
    isAdmin: bool = Field(default=False)
    isSuperuser: bool = Field(default=False)

    # Relationships
    # Verifiable Details
    domains: List["KnownDomains"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    knownIps: List["KnownIps"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    verifiedEmails: List["VerifiedEmail"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    verifiedDocuments: List["VerifiedDocuments"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    subscription: List["Subscription"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    cards: List["Card"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    bankAccounts: List["BankAccount"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    transactions: List["TransactionHistory"] = Relationship(
        back_populates="payer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    portfolios: List["Portfolio"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    staking: List["Staking"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    copyTrades: List["CopyTrading"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    arbitrage: List["ArbitrageRecords"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    @property
    def age(self) -> Optional[int]:
        if self.dob:
            today = datetime.today().date()
            age = today.year - self.dob.year - (
                (today.month, today.day) < (self.dob.month, self.dob.day)
            )
            return age
        return 1

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class KnownIps(SQLModel, table=True):
    __tablename__ = "known_ips"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    ip: IPvAnyAddress

    # Foreign Key to User
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional["KnownDomains"] = Relationship(back_populates="knownIps")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="knownIps")

    def __repr__(self) -> str:
        return f"<KnownIp {self.ip}>"


class KnownDomains(SQLModel, table=True):
    __tablename__ = "domains"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    domain: AnyHttpUrl

    # Foreign Key to User
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="domains")

    verifiedEmails: List["VerifiedEmail"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    verifiedDocuments: List["VerifiedDocuments"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    knownIps: List[KnownIps] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    # Financial Fields
    subscription: List["Subscription"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    cards: List["Card"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    bankAccounts: List["BankAccount"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    transactions: List["TransactionHistory"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    portfolios: List["Portfolio"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    plans: List["Plans"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    testimonials: List["Testimonial"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    faqs: List["FAQ"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    staking: List["Staking"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    copyTrades: List["CopyTrading"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )
    arbitrage: List["ArbitrageRecords"] = Relationship(
        back_populates="domain",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Domains {self.ip}>"


class VerifiedEmail(SQLModel, table=True):
    __tablename__ = "verified_emails"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    email: EmailStr = Field(nullable=False, unique=True, index=True, max_length=100)
    verifiedAt: datetime = Field(default_factory=datetime.utcnow)

    # Foreign Key to User
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="verifiedEmails")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="verifiedEmails")

    def __repr__(self) -> str:
        return f"<VerifiedEmail {self.email}>"


class VerifiedDocuments(SQLModel, table=True):
    __tablename__ = "verified_documents"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    name: str
    file: FileUrl
    approved: bool = Field(default=False)

    # Foreign Key to User
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="verifiedDocuments")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="verifiedDocuments")

    def __repr__(self) -> str:
        return f"<VerifiedDocument {self.name}>"


class BankAccount(SQLModel, table=True):
    __tablename__ = "bank_accounts"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    bankName: Optional[str] = Field(nullable=True, max_length=255)
    accountNumber: Optional[str] = Field(nullable=True, unique=True, max_length=20)
    sortCode: Optional[str] = Field(nullable=True, max_length=10)
    routingNumber: Optional[ABARoutingNumber]
    verified: bool = Field(default=False)

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="bankAccounts")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="card")

    def __repr__(self) -> str:
        return f"<BankAccount {self.account_number}>"


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    cardNumber: PaymentCardNumber
    expirationDate: date = Field(nullable=False)
    cvv: str = Field(nullable=False, max_length=3)

    valid: bool = Field(default=False)

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="cards")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="card")

    def __repr__(self) -> str:
        return f"<Card {self.cardNumber}>"


# Portfolio
class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolio"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    assetName: str = Field(nullable=False)
    assetSymbol: str

    balance: Decimal = Field(decimal_places=2, default=0.00)
    quantity: Decimal = Field(decimal_places=2, default=0.00)
    purchasePrice: Decimal = Field(decimal_places=6, default=0.00)
    currentPrice: Decimal = Field(decimal_places=6, default=0.00)

    symbol: Optional[str]
    walletAddress: Optional[str]
    exchange: Optional[str]
    dividendYield: Optional[Decimal] = Field(decimal_places=6, default=0.00)

    isCrypto: bool = Field(default=False)
    isStocks: bool = Field(default=False)

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="portfolios")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="portfolios")

    purchaseDate: date = Field(
        default_factory=date.today,
        sa_column=Column(pg.TIMESTAMP, default=date.today),
    )

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )


class Staking(SQLModel, table=True):
    __tablename__ = "staking"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    token: str
    symbol: str
    amountStaked: Decimal = Field(default=0.000000, decimal_places=6)
    interestRate: Decimal = Field(default=0.04, decimal_places=2)
    earnings: Decimal = Field(default=0.000000, decimal_places=6)

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="staking")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    user: Optional[User] = Relationship(back_populates="staking")
    duration: int = 360

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )


class ArbitrageRecords(SQLModel, table=True):
    # https://medium.com/@crjameson/how-to-write-an-automated-crypto-perp-trading-bot-in-python-with-less-than-100-lines-of-code-e6503910fadb
    __tablename__ = "arbitrage"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    pair: str
    lowestAmount: Decimal = Field(default=0.000000, decimal_places=6)
    highestAmount: Decimal = Field(default=0.000000, decimal_places=6)
    exchange: str
    leverage: int = Field(default=20)
    riskPerTradePercentage: int = Field(default=2)
    riskRewardRatio: int = Field(default=2)
    stopLossPercent: Decimal = Field(default=0.2, decimal_places=2)
    earnings: Decimal = Field(default=0.000000, decimal_places=6)

    # the length of the queue is the period of the donchian channel
    # 120 means we look at the last 120 prices, one request every 30 seconds = 1h timeframe
    DON_MAX_PERIOD: int = 12
    REQUEST_INTERVAL_SECONDS: int = 30

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="arbitrage")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    user: Optional[User] = Relationship(back_populates="arbitrage")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )

    @property
    def takeProfitPercent(self):
        return self.stopLossPercent * self.riskRewardRatio


class CopyTrading(SQLModel, table=True):
    __tablename__ = "copy_trading"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    symbol: str
    watchedWalletAddress: str
    walletAddress: str
    network: str #bnb, eth
    percentToTrade: Decimal = Field(default=0.04, decimal_places=6)
    earnings: Decimal = Field(default=0.000000, decimal_places=6)
    active: bool = Field(default=True)

    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="copyTrades")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    user: Optional[User] = Relationship(back_populates="copyTrades")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )


# Analytics Model
class Analytics(SQLModel, table=True):
    __tablename__ = "analytics"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    pathname: str = Field(nullable=False)
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )

    # Relationships to track page views
    pageViews: List["PageView"] = Relationship(
        back_populates="analytics", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"<Analytics {self.pathname}>"


class PageView(SQLModel, table=True):
    __tablename__ = "page_views"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    ip: str = Field(nullable=False)
    buttonsClicked: List[str] = Field(default=[])  # Track buttons clicked
    timeSpentInSeconds: int = Field(default=0)  # Store time spent in seconds
    date: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(pg.DATE, nullable=False))

    # Foreign Key to Analytics
    analyticsUid: uuid.UUID = Field(foreign_key="analytics.uid")
    analytics: "Analytics" = Relationship(back_populates="pageViews")

    def __repr__(self) -> str:
        return f"<PageView {self.ip} - {self.date}>"


# General Models
class Testimonial(SQLModel, table=True):
    __tablename__ = "testimonials"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    name: str
    work: str
    company: str
    image: str
    testimony: str
    rating: int

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="testimonials")

    def __repr__(self) -> str:
        return f"<Testimonial {self.name}>"


class FAQ(SQLModel, table=True):
    __tablename__ = "faqs"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    question: str
    answer: str
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="faqs")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )

    def __repr__(self) -> str:
        return f"<FAQ {self.question}>"


# Transactions Models
class PlanFeaturesLink(SQLModel, table=True):
    featureUid: Optional[uuid.UUID] = Field(default=None, foreign_key="plan_features.id", primary_key=True)
    planUid: Optional[uuid.UUID] = Field(default=None, foreign_key="plans.id", primary_key=True)


class PlanFeatures(SQLModel, table=True):
    __tablename__ = "plan_features"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    name: str
    featured: bool = Field(default=False)

    plans: List["PlanFeaturesLink"] = Relationship(back_populates="features", link_model=PlanFeaturesLink)

    def __repr__(self) -> str:
        return f"<PlanFeatures {self.name}>"


class Plans(SQLModel, table=True):
    __tablename__ = "plans"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )
    name: str
    description: str

    features: List[PlanFeaturesLink] = Relationship(back_populates="plans", link_model=PlanFeaturesLink)
    subscriptions: List["Subscription"] = Relationship(
        back_populates="plan",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    trialInDays: int = Field(default=60)
    amount: Decimal = Field(default=0.00)
    duration: int  # months
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="plans")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )


    def __repr__(self) -> str:
        return f"<Plans {self.name}>"


class Subscription(SQLModel, table=True):
    __tablename__ = "investment_subscription"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    status: TransactionStatus = Field(default=TransactionStatus.PENDING)

    planUid: Optional[uuid.UUID] = Field(default=None, foreign_key="plans.uid")
    plan: Optional[Plans] = Relationship(back_populates="subscriptions")

    # Foreign Key to User
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="subscription")
    userUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="subscription")

    paidDate: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    expiryDate: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )



    def __repr__(self) -> str:
        return f"<Subscription {self.estate.name}>"



class TransactionHistory(SQLModel, table=True):
    __tablename__ = "transactions"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4
        )
    )

    transactionId: str
    amountPaid: Decimal = Field(default=0.00, decimal_places=2)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)

    # Foreign Key to User
    transactionType: TransactionPaymentType = Field(default=TransactionPaymentType.DUES)
    method: TransactionPaymentMethod =  Field(default=TransactionPaymentMethod.CREDITCARD)
    domainUid: Optional[uuid.UUID] = Field(default=None, foreign_key="domains.uid")
    domain: Optional[KnownDomains] = Relationship(back_populates="transactions")
    payerUid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    payer: Optional[User] = Relationship(back_populates="transactions")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(pg.TIMESTAMP, default=datetime.now),
    )

    def __repr__(self) -> str:
        return f"<Transactions {self.transactionId}>"

