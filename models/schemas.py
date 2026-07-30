

from pydantic import BaseModel
from datetime import date

class PostBase(BaseModel):
    description: str
    date:date
    etat: bool=False
    idClient: int

    class Config:
        orm_mode = True


class CreatePost(PostBase):
    class Config:
        orm_mode = True
class ConnectAdmin(BaseModel):
    connected:bool=False
    class Config:
        orm_mode = True