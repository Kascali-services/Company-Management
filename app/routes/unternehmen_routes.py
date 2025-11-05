import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.person import Person
from app.models.unternehmen import Unternehmen
from app.schemas.unternehmen import UnternehmenCreate, UnternehmenWithPersons, UnternehmenResponse

# Configure logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():  # éviter double logging
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api/unternehmen", tags=["unternehmen"])

@router.get("/", response_model=dict)
async def get_unternehmen(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    sort_by: str | None = "name",
    sort_order: str | None = "asc",
    db: Session = Depends(get_db)
):
    try:
        logger.info("Start fetching companies (skip=%s, limit=%s, search=%s, sort_by=%s, sort_order=%s)",
                    skip, limit, search, sort_by, sort_order)

        query = db.query(Unternehmen)

        if search:
            logger.info("Applying search filter: %s", search)
            search_filter = or_(
                Unternehmen.name.ilike(f"%{search}%"),
                Unternehmen.stadt.ilike(f"%{search}%"),
                Unternehmen.plz.ilike(f"%{search}%"),
                Unternehmen.bundesland.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        total = query.count()
        logger.info("Total records found: %s", total)

        if sort_by and hasattr(Unternehmen, sort_by):
            order_column = getattr(Unternehmen, sort_by)
            query = query.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())
            logger.info("Sorting applied on %s (%s)", sort_by, sort_order)
        else:
            logger.warning("Invalid sort_by column: %s", sort_by)

        unternehmen_list = query.offset(skip).limit(limit).all()
        logger.info("Fetched %s companies from database", len(unternehmen_list))

        items = []
        for u in unternehmen_list:
            ansprechpartner_data = None
            if u.ansprechpartner_id:
                person = db.query(Person).filter(Person.id == u.ansprechpartner_id).first()
                if person:
                    ansprechpartner_data = person
                    logger.info("Found contact person for company id=%s", u.id)
            personen_data = u.personen if hasattr(u, "personen") else []
            items.append(
                UnternehmenWithPersons(**UnternehmenResponse.from_orm(u).dict(),
                                       ansprechpartner=ansprechpartner_data,
                                       personen=personen_data)
            )

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.exception("Error while fetching companies")
        raise


@router.post("/", response_model=UnternehmenResponse)
async def create_unternehmen(unternehmen: UnternehmenCreate, db: Session = Depends(get_db)):
    if unternehmen.ansprechpartner_id:
        person = db.query(Person).filter(Person.id == unternehmen.ansprechpartner_id).first()
        if not person or person.rolle != "Ansprechpartner":
            raise HTTPException(status_code=400, detail="Ungültiger Ansprechpartner")

    db_unternehmen = Unternehmen(**unternehmen.dict())
    db.add(db_unternehmen)
    db.commit()
    db.refresh(db_unternehmen)
    return db_unternehmen
