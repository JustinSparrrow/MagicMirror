from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True