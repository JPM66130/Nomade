from sqlalchemy import Column, Integer, String, Float
from db import Base

class Itineraire(Base):
    __tablename__ = "itineraires"

    id = Column(Integer, primary_key=True, index=True)

    depart = Column(String)
    arrivee = Column(String)

    lat_depart = Column(Float)
    lon_depart = Column(Float)
    lat_arrivee = Column(Float)
    lon_arrivee = Column(Float)

    distance_km = Column(Float)
    duree_min = Column(Float)
