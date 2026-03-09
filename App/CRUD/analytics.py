"""
analytics.py
------------
Read-only analytics / reporting queries.

Functions
---------
  get_case_evidence_witness_suspect – GET /cases/{case_id}/details (combined snapshot)
  get_crime_hotspots                – GET /analytics/hotspots
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from App.db.models import Address, CaseDetail
from App.schema.case import (
    CaseEvidenceWitnessSuspectResponse,
    CrimeHotspotItem,
    CrimeHotspotQuery,
    CrimeHotspotResponse,
    EvidenceRead,
    SuspectRead,
    SuspectStatus,
    WitnessRead,
)
from App.CRUD.common import build_person_summary, fetch_case

# ---------------------------------------------------------------------------
# Combined case snapshot
# ---------------------------------------------------------------------------

def get_case_evidence_witness_suspect(
    db: Session,
    case_id: int,
    open_date: date | None = None,
) -> CaseEvidenceWitnessSuspectResponse:
    """Return evidence, witnesses, and suspects in one snapshot for a case."""
    case = fetch_case(db, case_id, open_date)

    evidence = [
        EvidenceRead(
            evidence_id=cf.evidence.evidence_id,
            case_id=cf.case_id,
            open_date=cf.open_date,
            description=cf.evidence.description,
            collection_date=cf.evidence.collection_date,
            location_id=cf.evidence.location_id,
            evidence_type=None,
            collected_by=None,
        )
        for cf in case.collected_for_entries
    ]

    witnesses = [
        WitnessRead(
            witness_id=ti.witness_person_id,
            person=build_person_summary(ti.witness.person) if ti.witness and ti.witness.person else None,
            family_contact=ti.witness.family_contact if ti.witness else None,
            statement=ti.witness.testimony if ti.witness else None,
        )
        for ti in case.testifies_in_entries
    ]

    suspects = [
        SuspectRead(
            suspect_id=inv.suspect_person_id,
            person=build_person_summary(inv.suspect.person) if inv.suspect and inv.suspect.person else None,
            physical_description=inv.suspect.physical_description if inv.suspect else None,
            family_contact=inv.suspect.family_contact if inv.suspect else None,
            arrest_status=(
                SuspectStatus(inv.suspect.arrest_status)
                if inv.suspect and inv.suspect.arrest_status
                else None
            ),
            reason=None,
            linked_evidence_ids=[lt.evidence_id for lt in inv.suspect.linked_evidence] if inv.suspect else [],
        )
        for inv in case.involved_in_entries
    ]

    return CaseEvidenceWitnessSuspectResponse(
        case_id=case.case_id,
        open_date=case.open_date,
        evidence=evidence,
        witnesses=witnesses,
        suspects=suspects,
    )


# ---------------------------------------------------------------------------
# Crime hotspots
# ---------------------------------------------------------------------------

def get_crime_hotspots(
    db: Session,
    query: CrimeHotspotQuery,
) -> CrimeHotspotResponse:
    """Aggregate case counts by city with optional filters. Returns cities sorted by count desc."""
    q = (
        db.query(Address.city, func.count(CaseDetail.case_id).label("case_count"))
        .join(CaseDetail, CaseDetail.crime_location == Address.address_id)
    )

    if query.city:
        q = q.filter(Address.city.ilike(f"%{query.city}%"))
    if query.from_date:
        q = q.filter(CaseDetail.open_date >= query.from_date)
    if query.to_date:
        q = q.filter(CaseDetail.open_date <= query.to_date)

    rows = (
        q.group_by(Address.city)
        .order_by(func.count(CaseDetail.case_id).desc())
        .all()
    )

    items = [
        CrimeHotspotItem(city=row.city or "Unknown", case_count=row.case_count)
        for row in rows
        if row.city  # skip NULL cities
    ]

    return CrimeHotspotResponse(items=items)
