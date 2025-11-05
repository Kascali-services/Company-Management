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
        """
        Validate that the federal state (Bundesland) is one of the 16 German states.

        Args:
            v: The state value to validate

        Returns:
            str: The validated state value

        Raises:
            ValueError: If the state is not one of the 16 German federal states
        """
        from app.utils.constants import BUNDESLAENDER
        if v not in BUNDESLAENDER:
            raise ValueError('Invalid federal state: must be one of the 16 German states')
        return v


class UnternehmenResponse(UnternehmenCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


class UnternehmenWithPersons(UnternehmenResponse):
    personen: List[PersonResponse] = []
    ansprechpartner: Optional[PersonResponse] = None

