from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(String(10))
    goods_id = Column(String(10), unique=True, index=True)
    goods_name = Column(String(255), index=True)
    goods_ori_price = Column(Integer)
    goods_price = Column(Integer)
    goods_info = Column(String(4000))
    use_guide = Column(String(4000))
    exc_branch = Column(String(50))
    valid_end_type = Column(String(1))
    valid_end_date = Column(String(8))
    send_type = Column(String(1))
    image_path_s = Column(String(150))
    image_path_m = Column(String(150))
    image_path_b = Column(String(150))
    image_size_s_w = Column(Integer)
    image_size_s_h = Column(Integer)
    image_size_m_w = Column(Integer)
    image_size_m_h = Column(Integer)
    image_size_b_w = Column(Integer)
    image_size_b_h = Column(Integer)

class Dispatch(Base):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), nullable=False)
    event_name = Column(String(100), nullable=False)
    sales_manager = Column(String(50))
    client_requester = Column(String(50))
    requester_email = Column(String(100))
    
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product")

    mms_title = Column(String(50))
    mms_content = Column(String(2000))
    sender_phone = Column(String(20))
    
    quantity = Column(Integer, default=0)
    dispatch_datetime = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    recipients = relationship("Recipient", back_populates="dispatch")

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"))
    phone_number = Column(String(20), nullable=False, index=True)
    coupon_code = Column(String(50), unique=True, index=True)
    status = Column(String(20), default="미교환") # e.g., 미교환, 교환, 폐기
    
    dispatch = relationship("Dispatch", back_populates="recipients")
