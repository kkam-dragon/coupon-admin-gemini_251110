from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_product_by_goods_id(db: AsyncSession, goods_id: str):
    """
    goods_id를 기준으로 상품을 조회합니다.
    """
    result = await db.execute(select(models.Product).filter(models.Product.goods_id == goods_id))
    return result.scalars().first()

async def search_products_by_name(db: AsyncSession, product_name: str):
    """
    상품명(goods_name)에 검색어가 포함된 상품들을 조회합니다.
    """
    query = select(models.Product)
    if product_name:
        query = query.filter(models.Product.goods_name.contains(product_name))
    
    result = await db.execute(query)
    return result.scalars().all()

async def upsert_product(db: AsyncSession, product: schemas.ProductCreate):
    """
    상품 정보가 존재하면 업데이트하고, 존재하지 않으면 새로 생성합니다.
    (Update + Insert = Upsert)
    """
    db_product = await get_product_by_goods_id(db, goods_id=product.goods_id)
    
    if db_product:
        # 상품 정보 업데이트
        # Pydantic 모델의 dict에서 None 값을 제외하여 기존 값을 덮어쓰지 않도록 함
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
    else:
        # 새로운 상품 생성
        db_product = models.Product(**product.dict())
        db.add(db_product)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

