from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

from app.schemas.person import PersonResponse


class UnternehmenCreate(BaseModel):
    name: str
    bundesland: str
    stadt: str
    plz: str = Field(..., pattern=r'^\d{5}$')
    strasse: str
    hausnummer: str
    ansprechpartner_id: Optional[int] = None

    @field_validator('bundesland')
    def validate_bundesland(cls, v):
        from app.utils.constants import BUNDESLAENDER
        if v not in BUNDESLAENDER:
            raise ValueError('Ungültiges Bundesland')
        return v


class UnternehmenResponse(UnternehmenCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


class UnternehmenWithPersons(UnternehmenResponse):
    personen: List[PersonResponse] = []
    ansprechpartner: Optional[PersonResponse] = None

