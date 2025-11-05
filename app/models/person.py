# app/models/person.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Person(Base):
    """
    SQLAlchemy model representing a person associated with a company.

    Each person belongs to exactly one company (firma_id) and has one of two roles:
    - Ansprechpartner (main contact person): A company can have exactly one
    - Empfehler (referrer): A company can have multiple

    The funktion field specifies the person's job function:
    - Mitarbeiter (employee)
    - Azubi (trainee/apprentice)

    Attributes:
        id: Primary key
        vorname: First name
        nachname: Last name
        email: Email address (optional)
        telefon: Phone number (optional)
        funktion: Job function (Mitarbeiter or Azubi)
        rolle: Role (Ansprechpartner or Empfehler)
        firma_id: Foreign key to the company this person belongs to
        firma: Relationship to the company
    """
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, index=True)
    vorname = Column(String, nullable=False)
    nachname = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefon = Column(String, nullable=True)
    funktion = Column(String, nullable=False)
    rolle = Column(String, nullable=False)
    firma_id = Column(Integer, ForeignKey("unternehmen.id"), nullable=False)

    # Relationship to the company this person belongs to
    firma = relationship(
        "Unternehmen",
        back_populates="personen",
        foreign_keys=[firma_id]  # Explicitly specify the foreign key
    )
