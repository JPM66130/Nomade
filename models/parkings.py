from sqlalchemy import Column, Integer, String
from db import Base

class Parking(Base):
    __tablename__ = "parkings"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    ville = Column(String)
