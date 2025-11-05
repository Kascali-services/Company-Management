# app/models/unternehmen.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from .person import Person

class Unternehmen(Base):
    """
    SQLAlchemy model representing a company (Unternehmen).

    This model has a circular relationship with the Person model:
    - A company can have one main contact person (ansprechpartner)
    - A company can have multiple associated persons (personen)

    The ansprechpartner relationship uses post_update=True to handle
    the circular foreign key dependency, allowing SQLAlchemy to defer
    constraint checking until after the initial insert.

    Attributes:
        id: Primary key
        name: Company name
        bundesland: Federal state (one of 16 German states)
        stadt: City
        plz: Postal code (5 digits)
        strasse: Street name
        hausnummer: House number
        ansprechpartner_id: Foreign key to the main contact person
        ansprechpartner: Relationship to the main contact person
        personen: Relationship to all persons associated with this company
    """
    __tablename__ = "unternehmen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    bundesland = Column(String, nullable=False)
    stadt = Column(String, nullable=False)
    plz = Column(String(5), nullable=False)
    strasse = Column(String, nullable=False)
    hausnummer = Column(String, nullable=False)
    ansprechpartner_id = Column(Integer, ForeignKey("person.id"), nullable=True)

    # Relationship to the main contact person
    ansprechpartner = relationship(
        "Person",
        foreign_keys=[ansprechpartner_id],
        post_update=True
    )

    # Relationship to all persons associated with this company
    personen = relationship(
        "Person",
        back_populates="firma",
        foreign_keys=[Person.firma_id]
    )
