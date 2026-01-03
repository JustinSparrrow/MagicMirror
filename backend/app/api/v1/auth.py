from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import user_crud
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if user_crud.get_user_by_name(db, username):
        raise HTTPException(status_code=400, detail="Username exists")
    new_user = user_crud.create_user(db, username, password)
    return new_user

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_crud.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    access_token = auth_service.create_access_token(data={"user_id": user.id})
    return {
        "status": "success",
        "access_token": access_token,  # 给前端的 Token
        "token_type": "bearer",        # 标准协议类型
        "user_id": user.id             # 返回 ID 方便前端存储
    }

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_crud.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 颁发 Token
    token = auth_service.create_access_token(data={"user_id": user.id})
    return {
        "status": "success", 
        "access_token": token, 
        "token_type": "bearer",
        "user_id": user.id
    }

