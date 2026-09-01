from sqlalchemy import Column, Integer, String
from db import Base

class Peage(Base):
    __tablename__ = "peages"

    id = Column(Integer, primary_key=True, index=True)
    autoroute = Column(String)
    prix = Column(Integer)
