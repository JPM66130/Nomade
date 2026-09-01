from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.alertes import Alerte

router = APIRouter(prefix="/alertes", tags=["Alertes"])

@router.get("/")
def liste_alertes(db: Session = Depends(get_db)):
    return db.query(Alerte).all()
