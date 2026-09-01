from sqlalchemy import Column, Integer, String
from db import Base

class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    type = Column(String)
