try:
    from ..database import Base
except ImportError:
    from database import Base

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean, text


class Administrateur(Base):
    __tablename__ = "administrateur"

    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False)
    mdp = Column(String,nullable=False)
   
class Post(Base):
    __tablename__ = "post"

    id = Column(Integer,primary_key=True,nullable=False)
    description = Column(String,nullable=False)
    etat = Column(String, server_default='')
    date = Column(TIMESTAMP(timezone=False),nullable=False)
    idClient= Column(Integer, ForeignKey("client.id"))

class Client(Base):
    __tablename__ = "client"

    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False)
    nom = Column(String,nullable=False)
    numTel= Column(Integer,nullable=False)
    accessToken=Column(String,nullable=False)
    pageId=Column(Integer,nullable=False)
    expireDateToken=Column(TIMESTAMP(timezone=True),nullable=False)
    