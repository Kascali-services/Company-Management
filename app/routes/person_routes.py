from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.person import Person
from app.models.unternehmen import Unternehmen
from app.schemas.person import PersonCreate, PersonResponse

router = APIRouter(prefix="/api/personen", tags=["Personen"])


@router.post("/unternehmen/{unternehmen_id}", response_model=PersonResponse)
async def create_person(unternehmen_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    """
    Create a new person associated with a company.

    Args:
        unternehmen_id: ID of the company to associate the person with
        person: Person data to create
        db: Database session dependency

    Returns:
        PersonResponse: The newly created person

    Raises:
        HTTPException: 404 if the company is not found
        HTTPException: 400 if trying to add a second Ansprechpartner to a company
    """
    unternehmen = db.query(Unternehmen).filter(Unternehmen.id == unternehmen_id).first()
    if not unternehmen:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if a contact person already exists for this company
    if person.rolle == "Ansprechpartner":
        existing_ap = db.query(Person).filter(
            Person.firma_id == unternehmen_id,
            Person.rolle == "Ansprechpartner"
        ).first()
        if existing_ap:
            raise HTTPException(status_code=400, detail="Company already has a contact person")

    db_person = Person(**person.dict(), firma_id=unternehmen_id)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    # If this is a contact person, update the company's reference
    if person.rolle == "Ansprechpartner":
        unternehmen.ansprechpartner_id = db_person.id
        db.commit()

    return db_person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    """
    Update an existing person's information.

    Args:
        person_id: ID of the person to update
        person: Updated person data
        db: Database session dependency

    Returns:
        PersonResponse: The updated person

    Raises:
        HTTPException: 404 if the person is not found
        HTTPException: 400 if trying to change role to Ansprechpartner when company already has one
    """
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")

    # If changing role to Ansprechpartner, check if one already exists
    if person.rolle == "Ansprechpartner" and db_person.rolle != "Ansprechpartner":
        existing_ap = db.query(Person).filter(
            Person.firma_id == db_person.firma_id,
            Person.rolle == "Ansprechpartner",
            Person.id != person_id
        ).first()
        if existing_ap:
            raise HTTPException(status_code=400, detail="Company already has a contact person")

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
    """
    Delete a person from the database.

    If the person is a contact person (Ansprechpartner), the company's
    ansprechpartner_id reference is automatically cleared before deletion.

    Args:
        person_id: ID of the person to delete
        db: Database session dependency

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if the person is not found
    """
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Remove contact person reference if necessary
    if db_person.rolle == "Ansprechpartner":
        unternehmen = db.query(Unternehmen).filter(Unternehmen.id == db_person.firma_id).first()
        if unternehmen and unternehmen.ansprechpartner_id == person_id:
            unternehmen.ansprechpartner_id = None
            db.commit()

    db.delete(db_person)
    db.commit()
    return {"message": "Person deleted successfully"}
