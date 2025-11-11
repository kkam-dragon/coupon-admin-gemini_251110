from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional

# 상품 생성을 위한 스키마
class ProductCreate(BaseModel):
    cat_id: str | None = None
    goods_id: str
    goods_name: str
    brand_name: str | None = None
    goods_price: int | None = None
    discount_price: int | None = None
    discount_rate: int | None = None
    goods_info: str | None = None
    use_guide: str | None = None
    valid_end_date: str | None = None
    image_path_s: str | None = None
    image_path_m: str | None = None
    image_path_b: str | None = None
    exc_branch: str | None = None

# 상품 정보 조회를 위한 기본 스키마
class ProductBase(BaseModel):
    id: int
    cat_id: str | None = None
    goods_id: str
    goods_name: str
    brand_name: str | None = None
    goods_price: int | None = None
    discount_price: int | None = None
    discount_rate: int | None = None
    goods_info: str | None = None
    use_guide: str | None = None
    valid_end_date: str | None = None
    image_path_s: str | None = None
    image_path_m: str | None = None
    image_path_b: str | None = None
    exc_branch: str | None = None

# DB에서 읽어올 때 사용할 상품 스키마 (ID, 타임스탬프 및 프론트엔드용 필드 포함)
class Product(ProductBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 프론트엔드 호환성을 위한 필드
    name: str = Field(alias='goods_name')
    expiry: Optional[str] = Field(alias='valid_end_date')
    location: Optional[str] = Field(alias='exc_branch')

    @computed_field
    @property
    def price(self) -> str:
        if self.goods_price is not None:
            return f"{self.goods_price:,}원"
        return "가격 정보 없음"

    class Config:
        orm_mode = True # SQLAlchemy 모델과 매핑을 위함
        populate_by_name = True # alias를 사용하여 필드 매핑 활성화

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
