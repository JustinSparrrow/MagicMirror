from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.crud import makeup_crud
from app.database import get_db
from app.services import makeup_service
from app.models.makeup import MakeupTemplate

router = APIRouter(prefix="/makeup", tags=["Makeup"])

@router.post("/extract")
async def extract(
    user_id: int = Form(...), 
    name: str = Form("New Makeup"),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    content = await file.read()
    # 异步调用 Service
    res = await makeup_service.process_and_save(db, user_id, name, content, "static")
    if not res: 
        raise HTTPException(status_code=422, detail="Face not detected")
    return res

@router.get("/my-styles/{user_id}")
async def get_my_styles(user_id: int, db: Session = Depends(get_db)):
    styles = db.query(MakeupTemplate).filter(MakeupTemplate.user_id == user_id).order_by(MakeupTemplate.created_at.desc()).all()
    return styles

@router.delete("/delete/{template_id}")
async def delete_style(template_id: int, user_id: int, db: Session = Depends(get_db)):
    success = makeup_crud.delete_makeup(db, template_id, user_id, upload_root="static")
    if not success:
        raise HTTPException(status_code=404, detail="妆容不存在或无权删除")
    return {"status": "success", "message": "删除成功，物理空间已回收"}

@router.patch("/rename/{template_id}")
async def rename_style(template_id: int, user_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    updated = makeup_crud.rename_makeup(db, template_id, user_id, name)
    if updated:
        return {"status": "success", "data": updated}
    raise HTTPException(status_code=404, detail="更新失败")

