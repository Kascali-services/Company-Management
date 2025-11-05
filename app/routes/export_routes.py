from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.unternehmen import Unternehmen
from app.models.person import Person
import csv
import io
from openpyxl import Workbook

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/csv")
async def export_csv(db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    # Kopfzeile
    writer.writerow([
        'Unternehmen', 'Bundesland', 'Stadt', 'PLZ', 'Straße', 'Hausnummer',
        'Ansprechpartner Vorname', 'Ansprechpartner Nachname', 'Ansprechpartner Email',
        'Anzahl Empfehler'
    ])

    unternehmen_list = db.query(Unternehmen).all()
    for u in unternehmen_list:
        empfehler_count = db.query(Person).filter(
            Person.firma_id == u.id,
            Person.rolle == "Empfehler"
        ).count()

        ap_vorname = u.ansprechpartner.vorname if u.ansprechpartner else ""
        ap_nachname = u.ansprechpartner.nachname if u.ansprechpartner else ""
        ap_email = u.ansprechpartner.email if u.ansprechpartner else ""

        writer.writerow([
            u.name, u.bundesland, u.stadt, u.plz, u.strasse, u.hausnummer,
            ap_vorname, ap_nachname, ap_email, empfehler_count
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=unternehmen.csv"}
    )


@router.get("/excel")
async def export_excel(db: Session = Depends(get_db)):
    wb = Workbook()
    ws = wb.active
    ws.title = "Unternehmen"

    ws.append([
        'Unternehmen', 'Bundesland', 'Stadt', 'PLZ', 'Straße', 'Hausnummer',
        'Ansprechpartner Vorname', 'Ansprechpartner Nachname', 'Ansprechpartner Email',
        'Anzahl Empfehler'
    ])

    unternehmen_list = db.query(Unternehmen).all()
    for u in unternehmen_list:
        empfehler_count = db.query(Person).filter(
            Person.firma_id == u.id,
            Person.rolle == "Empfehler"
        ).count()

        ap_vorname = u.ansprechpartner.vorname if u.ansprechpartner else ""
        ap_nachname = u.ansprechpartner.nachname if u.ansprechpartner else ""
        ap_email = u.ansprechpartner.email if u.ansprechpartner else ""

        ws.append([
            u.name, u.bundesland, u.stadt, u.plz, u.strasse, u.hausnummer,
            ap_vorname, ap_nachname, ap_email, empfehler_count
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=unternehmen.xlsx"}
    )
