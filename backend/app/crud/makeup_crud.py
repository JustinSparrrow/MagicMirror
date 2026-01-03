import os
import shutil
from sqlalchemy.orm import Session
from app.models.makeup import MakeupTemplate

def save_makeup_record(db: Session, template_data: dict):
    db_item = MakeupTemplate(**template_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_template_by_md5(db: Session, user_id: int, md5: str):
    return db.query(MakeupTemplate).filter(
        MakeupTemplate.user_id == user_id,
        MakeupTemplate.source_md5 == md5
    ).first()

# --- 重点：智能删除函数 ---
def delete_makeup(db: Session, template_id: int, user_id: int, upload_root: str):
    # 1. 查找记录
    item = db.query(MakeupTemplate).filter(
        MakeupTemplate.id == template_id, 
        MakeupTemplate.user_id == user_id
    ).first()
    
    if not item:
        return False

    target_md5 = item.source_md5

    # 2. 从数据库执行删除
    db.delete(item)
    db.commit()

    # 3. 检查是否还有其他人（或其他记录）在用这个文件夹
    # 比如用户 A 删除了这张图，但用户 B 以前也上传过同一张图，我们就不能删物理文件
    remaining_count = db.query(MakeupTemplate).filter(
        MakeupTemplate.source_md5 == target_md5
    ).count()

    if remaining_count == 0:
        # 没有任何记录引用了，物理删除 static/makeup_parts/{md5} 文件夹
        folder_path = os.path.join(upload_root, "makeup_parts", target_md5)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"🧹 [Storage Cleanup] 物理文件已彻底删除: {target_md5}")
            except Exception as e:
                print(f"⚠️ [Cleanup Error] 物理删除失败: {e}")
    
    return True

def rename_makeup(db: Session, template_id: int, user_id: int, new_name: str):
    db_item = db.query(MakeupTemplate).filter(
        MakeupTemplate.id == template_id, 
        MakeupTemplate.user_id == user_id
    ).first()
    if db_item:
        db_item.template_name = new_name
        db.commit()
        db.refresh(db_item)
        return db_item
    return None
