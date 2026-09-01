from sqlalchemy import Column, Integer, String
from db import Base

class Pays(Base):
    __tablename__ = "pays"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
