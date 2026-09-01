from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.pays import Pays

router = APIRouter(prefix="/pays", tags=["Pays"])

@router.get("/")
def liste_pays(db: Session = Depends(get_db)):
    return db.query(Pays).all()

@router.post("/")
def ajouter_pays(nom: str, db: Session = Depends(get_db)):
    pays = Pays(nom=nom)
    db.add(pays)
    db.commit()
    db.refresh(pays)
    return pays
