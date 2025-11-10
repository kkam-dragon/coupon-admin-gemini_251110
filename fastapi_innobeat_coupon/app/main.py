from fastapi import FastAPI, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import uuid
from typing import List

from . import models, schemas
from .database import engine, Base, get_db

from fastapi.middleware.cors import CORSMiddleware

# 애플리케이션 시작 시 실행될 이벤트 핸들러
async def startup():
    async with engine.begin() as conn:
        # 모든 테이블 생성 (Product, Dispatch, Recipient)
        await conn.run_sync(Base.metadata.create_all)

    async for session in get_db():
        # 상품 데이터가 비어있는지 확인
        result = await session.execute(select(models.Product))
        if result.scalars().first() is None:
            # js/main.js의 샘플 데이터를 기반으로 초기 데이터 추가
            sample_products = [
                { "name": "불고기 버거 세트", "expiry": "60일", "price": "5,000 / 7,000원", "location": "전국 모든 매장" },
                { "name": "새우 버거 세트", "expiry": "60일", "price": "4,500 / 6,500원", "location": "전국 모든 매장" },
                { "name": "아메리카노 (R)", "expiry": "30일", "price": "2,000 / 3,000원", "location": "카페 A, 카페 B 전 지점" },
                { "name": "영화 관람권 (1인)", "expiry": "5년", "price": "10,000 / 15,000원", "location": "CGV, 롯데시네마, 메가박스" },
                { "name": "치킨 콤보", "expiry": "30일", "price": "18,000 / 22,000원", "location": "BBQ, BHC" },
                { "name": "피자 L 사이즈", "expiry": "30일", "price": "25,000 / 30,000원", "location": "도미노피자, 피자헛" },
                { "name": "편의점 5천원권", "expiry": "5년", "price": "4,500 / 5,000원", "location": "GS25, CU, 세븐일레븐" },
                { "name": "베이커리 1만원권", "expiry": "60일", "price": "9,000 / 10,000원", "location": "파리바게뜨, 뚜레쥬르" },
                { "name": "아이스크림 파인트", "expiry": "30일", "price": "7,000 / 8,200원", "location": "배스킨라빈스" },
                { "name": "주유 5천원 할인권", "expiry": "60일", "price": "0 / 5,000원", "location": "SK, GS칼텍스" },
                { "name": "서점 1만원 도서상품권", "expiry": "5년", "price": "9,500 / 10,000원", "location": "교보문고, 영풍문고" },
                { "name": "음악 스트리밍 1개월권", "expiry": "30일", "price": "7,900 / 8,900원", "location": "멜론, 지니뮤직" },
                { "name": "OTT 1개월 이용권", "expiry": "30일", "price": "12,000 / 14,000원", "location": "넷플릭스, 왓챠" },
                { "name": "특급호텔 숙박권", "expiry": "5년", "price": "250,000 / 300,000원", "location": "신라호텔, 롯데호텔" },
                { "name": "백화점 5만원 상품권", "expiry": "5년", "price": "48,000 / 50,000원", "location": "신세계, 롯데, 현대백화점" }
            ]
            for prod in sample_products:
                session.add(models.Product(**prod))
            await session.commit()
        break # 세션을 한 번만 사용하고 종료

app = FastAPI(on_startup=[startup])

# CORS 미들웨어 추가 (프론트엔드와 통신을 위함)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 실제 운영 환경에서는 특정 도메인만 허용해야 합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "쿠폰 관리 백엔드 API"}

@app.get("/api/products", response_model=List[schemas.Product])
async def get_products(db: AsyncSession = Depends(get_db)):
    """
    모든 상품 목록을 조회합니다.
    """
    result = await db.execute(select(models.Product))
    products = result.scalars().all()
    return products

@app.post("/api/dispatches", response_model=schemas.Dispatch)
async def create_dispatch(dispatch_data: schemas.DispatchCreate, db: AsyncSession = Depends(get_db)):
    """
    새로운 쿠폰 발송 요청을 생성합니다.
    """
    # 1. Dispatch(발송) 정보 생성
    db_dispatch = models.Dispatch(
        client_name=dispatch_data.client_name,
        event_name=dispatch_data.event_name,
        sales_manager=dispatch_data.sales_manager,
        client_requester=dispatch_data.client_requester,
        requester_email=dispatch_data.requester_email,
        product_id=dispatch_data.product_id,
        mms_title=dispatch_data.mms_title,
        mms_content=dispatch_data.mms_content,
        sender_phone=dispatch_data.sender_phone,
        dispatch_datetime=dispatch_data.dispatch_datetime,
        quantity=len(dispatch_data.recipients)
    )
    db.add(db_dispatch)
    await db.flush() # db_dispatch의 id를 가져오기 위해 flush

    # 2. Recipient(수신자) 정보 생성
    for recipient in dispatch_data.recipients:
        # 실제 쿠펀 API 연동 대신 UUID로 쿠폰 번호 생성
        coupon_code = str(uuid.uuid4().hex)[:12].upper()
        db_recipient = models.Recipient(
            dispatch_id=db_dispatch.id,
            phone_number=recipient.phone_number,
            coupon_code=coupon_code
        )
        db.add(db_recipient)

    await db.commit()
    await db.refresh(db_dispatch)

    # 3. [시뮬레이션] LG U+ MMS 발송 요청
    # logger.info(f"{db_dispatch.id}번 발송 건에 대해 MMS 발송 요청을 시뮬레이션합니다.")

    return db_dispatch
