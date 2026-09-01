from sqlalchemy import Column, Integer, String
from db import Base

class Restriction(Base):
    __tablename__ = "restrictions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    description = Column(String)
