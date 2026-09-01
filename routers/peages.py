from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.peages import Peage

router = APIRouter(prefix="/peages", tags=["Péages"])

@router.get("/")
def liste_peages(db: Session = Depends(get_db)):
    return db.query(Peage).all()
