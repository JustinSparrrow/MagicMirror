from app.services import ai_service
from app.crud import makeup_crud
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("Makeup_Service")

async def process_and_save(db: Session, user_id: int, template_name: str, img_bytes: bytes, upload_root: str):
    # 调用异步 AI 任务
    result = await ai_service.extract_face_parts_async(img_bytes, upload_root)
    
    if not result:
        return None
    
    urls, img_md5 = result

    # --- 核心：数据库去重逻辑 ---
    # 检查该用户是否已经保存过这个指纹的妆容
    existing_record = makeup_crud.get_template_by_md5(db, user_id, img_md5)
    
    if existing_record:
        logger.info(f"♻️ [DB Hint] 用户 {user_id} 已存过该妆容 (MD5: {img_md5})，跳过插入，直接返回旧记录。")
        return existing_record
    
    # 2. 如果不存在，则组装数据并存库
    logger.info(f"📝 [DB New] 为用户 {user_id} 创建新的妆容记录。")
    record_data = {
        "user_id": user_id,
        "template_name": template_name,
        "left_eye_path": urls.get("left_eye"),
        "right_eye_path": urls.get("right_eye"),
        "left_eyebrow_path": urls.get("left_eyebrow"),
        "right_eyebrow_path": urls.get("right_eyebrow"),
        "lips_path": urls.get("lips"),
        "nose_path": urls.get("nose")
    }
    return makeup_crud.save_makeup_record(db, record_data)
