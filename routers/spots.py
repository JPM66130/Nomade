from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.spots import Spot

router = APIRouter(prefix="/spots", tags=["Spots"])

@router.get("/")
def liste_spots(db: Session = Depends(get_db)):
    return db.query(Spot).all()
