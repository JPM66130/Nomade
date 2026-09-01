from sqlalchemy import Column, Integer, String
from db import Base

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    ville = Column(String)
