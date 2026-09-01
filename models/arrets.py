from sqlalchemy import Column, Float, ForeignKey, Integer, String

from db import Base


class Arret(Base):
    __tablename__ = "arrets"

    id = Column(Integer, primary_key=True, index=True)
    itineraire_id = Column(Integer, ForeignKey("itineraires.id"), nullable=False, index=True)
    nom = Column(String, nullable=False, default="Arrêt")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    direction_deg = Column(Float, nullable=False)
    precision_m = Column(Float, nullable=False)