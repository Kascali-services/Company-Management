import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.person import Person
from app.models.unternehmen import Unternehmen
from app.schemas.unternehmen import UnternehmenCreate, UnternehmenWithPersons, UnternehmenResponse

# Get logger for this module
logger = logging.getLogger(__name__)

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
    """
    Retrieve a paginated list of companies with optional search and sorting.

    Args:
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 20, max: 100)
        search: Optional search string to filter companies by name, city, postal code, or state
        sort_by: Field to sort by (default: "name"). Valid values: name, bundesland, stadt, plz
        sort_order: Sort direction (default: "asc"). Valid values: asc, desc
        db: Database session dependency

    Returns:
        dict: Paginated response containing:
            - items: List of companies with their associated persons
            - total: Total number of matching companies
            - skip: Number of records skipped
            - limit: Maximum number of records returned

    Raises:
        HTTPException: If database query fails
    """
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
    """
    Create a new company.

    Args:
        unternehmen: Company data to create
        db: Database session dependency

    Returns:
        UnternehmenResponse: The newly created company

    Raises:
        HTTPException: 400 if the specified contact person is invalid or doesn't have the
                       Ansprechpartner role
    """
    if unternehmen.ansprechpartner_id:
        person = db.query(Person).filter(Person.id == unternehmen.ansprechpartner_id).first()
        if not person or person.rolle != "Ansprechpartner":
            raise HTTPException(status_code=400, detail="Invalid contact person: must have Ansprechpartner role")

    db_unternehmen = Unternehmen(**unternehmen.dict())
    db.add(db_unternehmen)
    db.commit()
    db.refresh(db_unternehmen)
    return db_unternehmen
