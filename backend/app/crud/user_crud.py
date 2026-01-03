from sqlalchemy.orm import Session
from app.models.user import User
from passlib.context import CryptContext

# 初始化加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_name(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    # 安全性：哈希存储密码
    hashed = pwd_context.hash(password)
    db_user = User(username=username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    # 验证哈希值
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

