
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from . import models, schemas
from .config import settings  # 설정 파일에서 API 키 등을 가져오도록 구성

# 동기화 함수
async def sync_products_from_coufun(db: AsyncSession):
    """
    쿠펀 API에서 상품 정보를 가져와 DB에 동기화합니다.
    """
    print("상품 정보 동기화를 시작합니다...")

    # API 호출을 위한 정보 (설정 파일에서 가져와야 함)
    api_url = "https://api.coufun.co.kr/v2/b2c/goods/list" # 예시 URL
    headers = {
        "Authorization": f"Bearer {settings.COUPON_API_KEY}" 
    }
    params = {
        "cp_id": settings.COUPON_CP_ID,
        # 필요한 다른 파라미터들 추가
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=params)
            response.raise_for_status() # 오류 발생 시 예외 처리
            
            api_data = response.json()
            
            if api_data.get("res_code") == "0000":
                products_data = api_data.get("goods_list", [])
                
                # 1. 기존 상품 정보 모두 삭제
                await db.execute(delete(models.Product))
                
                # 2. 새로운 상품 정보 추가
                for item in products_data:
                    product = models.Product(
                        cat_id=item.get("CAT_ID"),
                        goods_id=item.get("GOODS_ID"),
                        goods_name=item.get("GOODS_NAME"),
                        goods_ori_price=int(item.get("GOODS_ORI_PRICE", 0)),
                        goods_price=int(item.get("GOODS_PRICE", 0)),
                        goods_info=item.get("GOODS_INFO"),
                        use_guide=item.get("USE_GUIDE"),
                        exc_branch=item.get("EXC_BRANCH"),
                        valid_end_type=item.get("VALID_END_TYPE"),
                        valid_end_date=item.get("VALID_END_DATE"),
                        send_type=item.get("SEND_TYPE"),
                        image_path_s=item.get("IMAGE_PATH_S"),
                        image_path_m=item.get("IMAGE_PATH_M"),
                        image_path_b=item.get("IMAGE_PATH_B"),
                        image_size_s_w=int(item.get("IMAGE_SIZE_S_W", 0)),
                        image_size_s_h=int(item.get("IMAGE_SIZE_S_H", 0)),
                        image_size_m_w=int(item.get("IMAGE_SIZE_M_W", 0)),
                        image_size_m_h=int(item.get("IMAGE_SIZE_M_H-", 0)), # 문서 오타 수정
                        image_size_b_w=int(item.get("IMAGE_SIZE_B_W", 0)),
                        image_size_b_h=int(item.get("IMAGE_SIZE_B_H", 0)),
                    )
                    db.add(product)
                
                await db.commit()
                print(f"상품 {len(products_data)}개 동기화 완료.")
            else:
                print(f"API 오류: {api_data.get('res_msg')}")

    except httpx.RequestError as e:
        print(f"API 요청 중 오류 발생: {e}")
    except Exception as e:
        print(f"동기화 중 알 수 없는 오류 발생: {e}")
        await db.rollback()

