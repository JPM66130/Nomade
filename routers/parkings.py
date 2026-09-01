from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.parkings import Parking

router = APIRouter(prefix="/parkings", tags=["Parkings"])

@router.get("/")
def liste_parkings(db: Session = Depends(get_db)):
    return db.query(Parking).all()
