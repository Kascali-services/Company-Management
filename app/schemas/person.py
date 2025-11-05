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
        """
        Validate that the person's function is either Mitarbeiter or Azubi.

        Args:
            v: The function value to validate

        Returns:
            str: The validated function value

        Raises:
            ValueError: If the function is not 'Mitarbeiter' or 'Azubi'
        """
        if v not in ['Mitarbeiter', 'Azubi']:
            raise ValueError('Function must be either Mitarbeiter (employee) or Azubi (trainee)')
        return v

    @field_validator('rolle')
    def validate_rolle(cls, v):
        """
        Validate that the person's role is either Empfehler or Ansprechpartner.

        Args:
            v: The role value to validate

        Returns:
            str: The validated role value

        Raises:
            ValueError: If the role is not 'Empfehler' or 'Ansprechpartner'
        """
        if v not in ['Empfehler', 'Ansprechpartner']:
            raise ValueError('Role must be either Empfehler (referrer) or Ansprechpartner (contact person)')
        return v


class PersonResponse(PersonCreate):
    id: int
    firma_id: int

    model_config = {
        "from_attributes": True
    }
