from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.person import Person
from app.models.unternehmen import Unternehmen
from app.schemas.person import PersonCreate, PersonResponse

router = APIRouter(prefix="/api/personen", tags=["Personen"])


@router.post("/unternehmen/{unternehmen_id}", response_model=PersonResponse)
async def create_person(unternehmen_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    unternehmen = db.query(Unternehmen).filter(Unternehmen.id == unternehmen_id).first()
    if not unternehmen:
        raise HTTPException(status_code=404, detail="Unternehmen nicht gefunden")

    # Prüfen, ob ein Ansprechpartner bereits existiert
    if person.rolle == "Ansprechpartner":
        existing_ap = db.query(Person).filter(
            Person.firma_id == unternehmen_id,
            Person.rolle == "Ansprechpartner"
        ).first()
        if existing_ap:
            raise HTTPException(status_code=400, detail="Unternehmen hat bereits einen Ansprechpartner")

    db_person = Person(**person.dict(), firma_id=unternehmen_id)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    # Falls Ansprechpartner, Unternehmen aktualisieren
    if person.rolle == "Ansprechpartner":
        unternehmen.ansprechpartner_id = db_person.id
        db.commit()

    return db_person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")

    # Wenn Rolle geändert wird, prüfen, ob ein Ansprechpartner schon existiert
    if person.rolle == "Ansprechpartner" and db_person.rolle != "Ansprechpartner":
        existing_ap = db.query(Person).filter(
            Person.firma_id == db_person.firma_id,
            Person.rolle == "Ansprechpartner",
            Person.id != person_id
        ).first()
        if existing_ap:
            raise HTTPException(status_code=400, detail="Unternehmen hat bereits einen Ansprechpartner")

    for key, value in person.dict().items():
        setattr(db_person, key, value)

    db.commit()
    db.refresh(db_person)

    unternehmen = db.query(Unternehmen).filter(Unternehmen.id == db_person.firma_id).first()
    if person.rolle == "Ansprechpartner":
        unternehmen.ansprechpartner_id = db_person.id
    elif db_person.rolle == "Ansprechpartner" and person.rolle != "Ansprechpartner":
        if unternehmen.ansprechpartner_id == person_id:
            unternehmen.ansprechpartner_id = None
    db.commit()

    return db_person


@router.delete("/{person_id}")
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")

    # Ansprechpartner-Verknüpfung entfernen, falls nötig
    if db_person.rolle == "Ansprechpartner":
        unternehmen = db.query(Unternehmen).filter(Unternehmen.id == db_person.firma_id).first()
        if unternehmen and unternehmen.ansprechpartner_id == person_id:
            unternehmen.ansprechpartner_id = None
            db.commit()

    db.delete(db_person)
    db.commit()
    return {"message": "Person gelöscht"}
