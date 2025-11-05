# app/models/unternehmen.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from .person import Person

class Unternehmen(Base):
    __tablename__ = "unternehmen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    bundesland = Column(String, nullable=False)
    stadt = Column(String, nullable=False)
    plz = Column(String(5), nullable=False)
    strasse = Column(String, nullable=False)
    hausnummer = Column(String, nullable=False)
    ansprechpartner_id = Column(Integer, ForeignKey("person.id"), nullable=True)

    # Relation vers le contact principal
    ansprechpartner = relationship(
        "Person",
        foreign_keys=[ansprechpartner_id],
        post_update=True
    )

    # Relation vers toutes les personnes liées à l'entreprise
    personen = relationship(
        "Person",
        back_populates="firma",
        foreign_keys=[Person.firma_id]
    )
