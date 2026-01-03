from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from app.database import Base
import datetime

class MakeupTemplate(Base):
    __tablename__ = "makeup_templates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_md5 = Column(String, index=True) 
    template_name = Column(String)
    left_eye_path = Column(String)
    right_eye_path = Column(String)
    left_eyebrow_path = Column(String)
    right_eyebrow_path = Column(String)
    lips_path = Column(String)
    nose_path = Column(String)
    rating = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
