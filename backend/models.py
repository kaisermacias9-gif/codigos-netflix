from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

class ServiceType(str, Enum):
    NETFLIX = "NETFLIX"
    AMAZON_PRIME = "AMAZON PRIME"
    DISNEY_PLUS = "DISNEY+"
    HBO_MAX = "HBO MAX"
    SPOTIFY = "SPOTIFY"
    YOUTUBE_PREMIUM = "YOUTUBE PREMIUM"
    APPLE_TV_PLUS = "APPLE TV+"
    PARAMOUNT_PLUS = "PARAMOUNT+"

class SubscriberStatus(str, Enum):
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"

class MessageType(str, Enum):
    RECORDATORIO = "recordatorio"
    VENCIMIENTO = "vencimiento"
    PERSONALIZADO = "personalizado"

class MessageStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"

# Base Models
class SubscriberBase(BaseModel):
    service: ServiceType
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=9, max_length=15)
    email: EmailStr
    expirationDate: date

    @validator('name')
    def validate_name(cls, v):
        return v.strip().upper()

    @validator('phone')
    def validate_phone(cls, v):
        # Remove any non-digit characters
        phone_clean = ''.join(filter(str.isdigit, v))
        if len(phone_clean) < 9:
            raise ValueError('Phone number must have at least 9 digits')
        return phone_clean

class SubscriberCreate(SubscriberBase):
    pass

class SubscriberUpdate(BaseModel):
    service: Optional[ServiceType] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    expirationDate: Optional[date] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            return v.strip().upper()
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_clean = ''.join(filter(str.isdigit, v))
            if len(phone_clean) < 9:
                raise ValueError('Phone number must have at least 9 digits')
            return phone_clean
        return v

class Subscriber(SubscriberBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: SubscriberStatus
    daysRemaining: int
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class MessageLogCreate(BaseModel):
    subscriberId: str
    messageType: MessageType
    message: Optional[str] = None

class MessageLog(MessageLogCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: MessageStatus
    sentAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total: int
    expiring: int
    active: int
    expired: int
    revenue: float

class SubscribersResponse(BaseModel):
    subscribers: List[Subscriber]
    total: int

class ServicesResponse(BaseModel):
    services: List[str]

class MessageResponse(BaseModel):
    success: bool
    message: str
    messageLog: Optional[MessageLog] = None