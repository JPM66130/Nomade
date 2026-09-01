from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.stations import Station

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("/")
def liste_stations(db: Session = Depends(get_db)):
    return db.query(Station).all()
