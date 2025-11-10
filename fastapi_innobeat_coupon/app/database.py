import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# docker-compose.yml에서 설정한 환경 변수 사용
DB_HOST = os.getenv("DB_HOST", "mariadb_innobeat_coupon")
DB_USER = os.getenv("DB_USER", "coupon_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "coupon_pass")
DB_NAME = os.getenv("DB_NAME", "innobeat_coupon_db")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 생성
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# SQLAlchemy 모델의 베이스 클래스
Base = declarative_base()

# API 요청 처리 중 DB 세션을 제공하는 의존성 함수
async def get_db():
    async with SessionLocal() as session:
        yield session
