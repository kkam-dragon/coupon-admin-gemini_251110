from pydantic import BaseModel
from datetime import datetime

# 상품 정보 조회를 위한 기본 스키마
class ProductBase(BaseModel):
    name: str
    expiry: str | None = None
    price: str | None = None
    location: str | None = None

# DB에서 읽어올 때 사용할 상품 스키마 (ID 포함)
class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True # SQLAlchemy 모델과 매핑을 위함

# 수신자 생성 스키마
class RecipientCreate(BaseModel):
    phone_number: str

# 발송 기본 스키마
class DispatchBase(BaseModel):
    client_name: str
    event_name: str
    sales_manager: str
    client_requester: str
    requester_email: str
    product_id: int
    mms_title: str
    mms_content: str
    sender_phone: str
    dispatch_datetime: datetime

# 발송 생성 스키마 (API 요청 본문)
class DispatchCreate(DispatchBase):
    recipients: list[RecipientCreate]

# 발송 응답 스키마
class Dispatch(DispatchBase):
    id: int
    quantity: int

    class Config:
        orm_mode = True
