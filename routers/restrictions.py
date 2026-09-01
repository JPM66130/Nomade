from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.restrictions import Restriction

router = APIRouter(prefix="/restrictions", tags=["Restrictions"])

@router.get("/")
def liste_restrictions(db: Session = Depends(get_db)):
    return db.query(Restriction).all()
