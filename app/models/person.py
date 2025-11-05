# app/models/person.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, index=True)
    vorname = Column(String, nullable=False)
    nachname = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefon = Column(String, nullable=True)
    funktion = Column(String, nullable=False)
    rolle = Column(String, nullable=False)
    firma_id = Column(Integer, ForeignKey("unternehmen.id"), nullable=False)

    # Relation vers l'entreprise
    firma = relationship(
        "Unternehmen",
        back_populates="personen",
        foreign_keys=[firma_id]  # <-- préciser explicitement la FK
    )
