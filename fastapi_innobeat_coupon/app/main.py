from fastapi import FastAPI, Depends, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import uuid
from typing import List, Optional

from . import models, schemas, crud
from .database import engine, Base, get_db

from fastapi.middleware.cors import CORSMiddleware

# 애플리케이션 시작 시 실행될 이벤트 핸들러
async def startup():
    async with engine.begin() as conn:
        # 개발 환경용: 기존 테이블을 모두 삭제하여 스키마 변경을 쉽게 적용합니다.
        # 주의: 운영 환경에서는 이 코드를 반드시 제거해야 합니다.
        # await conn.run_sync(Base.metadata.drop_all)
        # 모든 테이블 생성 (Product, Dispatch, Recipient)
        await conn.run_sync(Base.metadata.create_all)

    # 비동기 세션을 사용하여 초기 데이터 삽입
    async for session in get_db():
        try:
            # 상품 데이터가 비어있는지 확인
            result = await session.execute(select(models.Product))
            if result.scalars().first() is None:
                # js/main.js의 샘플 데이터를 기반으로 초기 데이터 추가
                sample_products = [
                    { "goods_id": "P0001", "goods_name": "불고기 버거 세트", "valid_end_date": "60일", "goods_price": 7000, "exc_branch": "전국 모든 매장" },
                    { "goods_id": "P0002", "goods_name": "새우 버거 세트", "valid_end_date": "60일", "goods_price": 6500, "exc_branch": "전국 모든 매장" },
                    { "goods_id": "P0003", "goods_name": "아메리카노 (R)", "valid_end_date": "30일", "goods_price": 3000, "exc_branch": "카페 A, 카페 B 전 지점" },
                    { "goods_id": "P0004", "goods_name": "영화 관람권 (1인)", "valid_end_date": "5년", "goods_price": 15000, "exc_branch": "CGV, 롯데시네마, 메가박스" },
                    { "goods_id": "P0005", "goods_name": "치킨 콤보", "valid_end_date": "30일", "goods_price": 22000, "exc_branch": "BBQ, BHC" },
                    { "goods_id": "P0006", "goods_name": "피자 L 사이즈", "valid_end_date": "30일", "goods_price": 30000, "exc_branch": "도미노피자, 피자헛" },
                    { "goods_id": "P0007", "goods_name": "편의점 5천원권", "valid_end_date": "5년", "goods_price": 5000, "exc_branch": "GS25, CU, 세븐일레븐" },
                    { "goods_id": "P0008", "goods_name": "베이커리 1만원권", "valid_end_date": "60일", "goods_price": 10000, "exc_branch": "파리바게뜨, 뚜레쥬르" },
                    { "goods_id": "P0009", "goods_name": "아이스크림 파인트", "valid_end_date": "30일", "goods_price": 8200, "exc_branch": "배스킨라빈스" },
                    { "goods_id": "P0010", "goods_name": "주유 5천원 할인권", "valid_end_date": "60일", "goods_price": 5000, "exc_branch": "SK, GS칼텍스" },
                    { "goods_id": "P0011", "goods_name": "서점 1만원 도서상품권", "valid_end_date": "5년", "goods_price": 10000, "exc_branch": "교보문고, 영풍문고" },
                    { "goods_id": "P0012", "goods_name": "음악 스트리밍 1개월권", "valid_end_date": "30일", "goods_price": 8900, "exc_branch": "멜론, 지니뮤직" },
                    { "goods_id": "P0013", "goods_name": "OTT 1개월 이용권", "valid_end_date": "30일", "goods_price": 14000, "exc_branch": "넷플릭스, 왓챠" },
                    { "goods_id": "P0014", "goods_name": "특급호텔 숙박권", "valid_end_date": "5년", "goods_price": 300000, "exc_branch": "신라호텔, 롯데호텔" },
                    { "goods_id": "P0015", "goods_name": "백화점 5만원 상품권", "valid_end_date": "5년", "goods_price": 50000, "exc_branch": "신세계, 롯데, 현대백화점" }
                ]
                for prod_data in sample_products:
                    session.add(models.Product(**prod_data))
                await session.commit()
        finally:
            # 세션을 한 번만 사용하고 종료
            break 

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
async def get_products(q: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    상품 목록을 조회합니다.
    - q (query string): 상품명(goods_name)으로 검색할 수 있습니다.
    """
    return await crud.search_products_by_name(db, product_name=q)


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
