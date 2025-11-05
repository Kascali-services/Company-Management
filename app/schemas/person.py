from pydantic import BaseModel, field_validator
from typing import Optional

class PersonCreate(BaseModel):
    vorname: str
    nachname: str
    email: Optional[str] = None
    telefon: Optional[str] = None
    funktion: str
    rolle: str

    @field_validator('funktion')
    def validate_funktion(cls, v):
        if v not in ['Mitarbeiter', 'Azubi']:
            raise ValueError('Funktion muss Mitarbeiter oder Azubi sein')
        return v

    @field_validator('rolle')
    def validate_rolle(cls, v):
        if v not in ['Empfehler', 'Ansprechpartner']:
            raise ValueError('Rolle muss Empfehler oder Ansprechpartner sein')
        return v


class PersonResponse(PersonCreate):
    id: int
    firma_id: int

    model_config = {
        "from_attributes": True
    }
