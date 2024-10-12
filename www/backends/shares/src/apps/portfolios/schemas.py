from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, condecimal


class PortfolioBase(BaseModel):
    assetName: str
    assetSymbol: str
    symbol: Optional[str]
    walletAddress: Optional[str]
    exchange: Optional[str]
    dividendYield: Annotated[Decimal, condecimal(ge=0, decimal_places=6)] = Decimal(0.00)  # Use Decimal for yields


class PortfolioUpdate(BaseModel):
    balance: Annotated[Decimal, condecimal(ge=0, decimal_places=6)]
    quantity: Optional[int]
    purchasePrice: Annotated[Decimal, condecimal(ge=0, decimal_places=6)]
    currentPrice: Annotated[Decimal, condecimal(ge=0, decimal_places=6)]


class PortfolioRead(PortfolioBase):
    uid: uuid.UUID
    isCrypto: bool
    isStocks: bool

    domainUid: Optional[uuid.UUID]
    userUid: Optional[uuid.UUID]

    purchaseDate: datetime
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
