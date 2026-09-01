from sqlalchemy import Column, ForeignKey, Integer, String, Text

from db import Base


class TrajetDetail(Base):
    __tablename__ = "trajet_details"

    id = Column(Integer, primary_key=True, index=True)
    itineraire_id = Column(Integer, ForeignKey("itineraires.id"), nullable=False, unique=True, index=True)
    nom_tournee = Column(String, nullable=False, default="Tournée sans nom")
    profil = Column(String, nullable=False)
    geometry_json = Column(Text, nullable=False)