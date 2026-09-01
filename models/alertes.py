from sqlalchemy import Column, Integer, String
from db import Base

class Alerte(Base):
    __tablename__ = "alertes"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    message = Column(String, nullable=False)
