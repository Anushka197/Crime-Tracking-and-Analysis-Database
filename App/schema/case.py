from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from pydantic import Field, model_validator
from App.schema.core import *

#--------------Enumerations and Constants--------------
class CaseStatus(str, Enum):
    """Enumeration of possible case statuses."""
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"

class CaseInclude(str, Enum):
    """Enumeration of related data that can be included in case responses."""
    EVIDENCE = "evidence"
    WITNESSES = "witnesses"
    SUSPECTS = "suspects"
    TRIALS = "trials"
    VICTIMS = "victims"
    TESTIMONIES = "testimonies"


class SuspectStatus(str, Enum):
    """Enumeration of possible suspect arrest statuses."""
    WANTED = "wanted"
    ARRESTED = "arrested"
    RELEASED = "released"


class CaseSortBy(str, Enum):
    """Enumeration of case list sorting options."""
    OPEN_DATE_ASC = "open_date"
    OPEN_DATE_DESC = "-open_date"
    CRIME_DATE_ASC = "crime_date"
    CRIME_DATE_DESC = "-crime_date"
    STATUS_ASC = "status"
    STATUS_DESC = "-status"


#--------------Case Schemas--------------
class CaseKey(SchemaModel):
    """Input: Unique case identifier with case ID and open date."""
    case_id: int = Field(..., gt=0)
    open_date: date


class PersonReferenceInput(SchemaModel):
    """Input: Reference to a person by ID or create new person inline."""
    person_id: int | None = Field(default=None, gt=0)
    person: PersonCreate | None = None

    @model_validator(mode="after")
    def validate_person_reference(self) -> PersonReferenceInput:
        has_person_id = self.person_id is not None
        has_person = self.person is not None
        if has_person_id == has_person:
            raise ValueError("Provide exactly one of person_id or person.")
        return self


class CaseOpenRequest(SchemaModel):
    """Input: Request to open a new case with crime details."""
    summary: str = Field(..., max_length=255, description="Maps to case_details.complaint_detail.")
    crime_type: str = Field(..., max_length=50)
    location_id: int = Field(..., gt=0, description="Maps to case_details.crime_location.")
    reported_by: int = Field(..., gt=0, description="Maps to case_details.personid.")
    initial_officer_id: int | None = Field(default=None, gt=0)
    occurred_at: date = Field(..., description="Maps to case_details.crime_date.")
    open_date: date | None = None

class CaseOpenResponse(SchemaModel):
    """Response: Newly created case with assigned ID and open date."""
    case_id: int = Field(..., gt=0)
    open_date: date
    status: CaseStatus = CaseStatus.OPEN
    summary: str | None = Field(default=None, max_length=255)


class CaseUpdateRequest(SchemaModel):
    """Input: Request to update existing case details."""
    summary: str | None = Field(default=None, max_length=255)
    crime_type: str | None = Field(default=None, max_length=50)
    location_id: int | None = Field(default=None, gt=0)
    reported_by: int | None = Field(default=None, gt=0)
    occurred_at: date | None = None
    status: CaseStatus | None = None
    assigned_officer_id: int | None = Field(default=None, gt=0)
    end_date: date | None = None


class CaseCloseRequest(SchemaModel):
    """Input: Request to close an open case with summary and date."""
    closing_summary: str | None = Field(default=None, max_length=255)
    closed_at: date | None = None


class CaseCloseResponse(SchemaModel):
    """Response: Case closure confirmation with end date and summary."""
    case_id: int = Field(..., gt=0)
    open_date: date
    status: CaseStatus = CaseStatus.CLOSED
    end_date: date | None = None
    closing_summary: str | None = Field(default=None, max_length=255)


class CaseRead(SchemaModel):
    """Response: Complete case details including assigned officers."""
    case_id: int = Field(..., gt=0)
    open_date: date
    crime_date: date | None = None
    end_date: date | None = None
    summary: str | None = Field(default=None, max_length=255, description="Case complaint/summary text.")
    crime_type: str | None = Field(default=None, max_length=50)
    location_id: int | None = Field(default=None, gt=0)
    status: CaseStatus | None = None
    reported_by: int | None = Field(default=None, gt=0)
    reporter: PersonSummary | None = None
    location: AddressRead | None = None
    assigned_officer_ids: list[int] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CaseOfficer(SchemaModel):
    """Link between case and assigned officer."""
    case_id: int = Field(..., gt=0)
    person_id: int = Field(..., gt=0)
    assigned_at: datetime | None = None


class CaseDetailResponse(SchemaModel):
    """Response: Case with all related evidence, witnesses, suspects, victims, and trials."""
    case: CaseRead
    included: list[CaseInclude] = Field(default_factory=list)
    evidence: list["EvidenceRead"] = Field(default_factory=list)
    witnesses: list["WitnessRead"] = Field(default_factory=list)
    suspects: list["SuspectRead"] = Field(default_factory=list)
    victims: list["VictimRead"] = Field(default_factory=list)
    trials: list["TrialRead"] = Field(default_factory=list)
    testimonies: list["TestimonyRead"] = Field(default_factory=list)


class CaseListQuery(SchemaModel):
    """Input: Query parameters to filter and paginate case listings."""
    crime_type: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=100)
    status: CaseStatus | None = None
    from_date: date | None = Field(default=None, alias="from")
    to_date: date | None = Field(default=None, alias="to")
    sort: CaseSortBy = CaseSortBy.OPEN_DATE_DESC
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)

    @model_validator(mode="after")
    def validate_date_range(self) -> CaseListQuery:
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date cannot be later than to_date.")
        return self


class CaseListItem(SchemaModel):
    """Response: Summary item for a case in list view."""
    case_id: int = Field(..., gt=0)
    open_date: date
    crime_date: date | None = None
    crime_type: str | None = Field(default=None, max_length=50)
    status: CaseStatus | None = None
    city: str | None = Field(default=None, max_length=100)


class CaseListResponse(SchemaModel):
    """Response: Paginated list of case items with metadata."""
    items: list[CaseListItem] = Field(default_factory=list)
    meta: PageMeta = Field(default_factory=PageMeta)


class TrialKey(SchemaModel):
    """Input: Unique trial identifier by trial number."""
    trial_id: int = Field(..., gt=0, description="Maps to trial.trial_number.")


#---------------Evidence schemas---------------

class CaseEvidenceCreateRequest(SchemaModel):
    """Input: Request to add evidence to a case."""
    evidence_type: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    collected_by: int | None = Field(default=None, gt=0)
    collected_at: date | None = Field(default=None, description="Maps to evidence.collection_date.")
    location_id: int | None = Field(default=None, gt=0, description="Maps to evidence.location_id.")


class EvidenceRead(SchemaModel):
    """Response: Evidence details including collection date and location."""
    evidence_id: int = Field(..., gt=0)
    case_id: int = Field(..., gt=0)
    open_date: date
    description: str | None = Field(default=None, max_length=255)
    collection_date: date | None = None
    location_id: int | None = Field(default=None, gt=0)
    evidence_type: str | None = Field(default=None, max_length=50)
    collected_by: int | None = Field(default=None, gt=0)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CaseEvidenceCreateResponse(SchemaModel):
    """Response: Newly created evidence with assigned ID and details."""
    evidence_id: int = Field(..., gt=0)
    evidence: EvidenceRead


class CaseEvidenceListResponse(SchemaModel):
    """Response: List of all evidence items for a case."""
    case_id: int = Field(..., gt=0)
    open_date: date
    items: list[EvidenceRead] = Field(default_factory=list)


#----------------Witness Schemas----------------
class CaseWitnessCreateRequest(PersonReferenceInput):
    """Input: Request to add witness to case with contact and statement."""
    contact_info: str | None = Field(
        default=None,
        max_length=15,
        description="Maps to witness.family_contact.",
    )
    statement: str | None = Field(default=None, max_length=255, description="Maps to witness.testimony.")


class WitnessRead(SchemaModel):
    """Response: Witness information with contact and statement."""
    witness_id: int = Field(..., gt=0, description="Person id used as witness primary key.")
    person: PersonSummary | None = None
    family_contact: str | None = Field(default=None, max_length=15)
    statement: str | None = Field(default=None, max_length=255)


class CaseWitnessCreateResponse(SchemaModel):
    """Response: Newly added witness with assigned ID and details."""
    witness_id: int = Field(..., gt=0)
    witness: WitnessRead


class CaseWitnessListResponse(SchemaModel):
    """Response: List of all witnesses in a case."""
    case_id: int = Field(..., gt=0)
    open_date: date
    items: list[WitnessRead] = Field(default_factory=list)


class WitnessTestimonyCreateRequest(SchemaModel):
    """Input: Request to record witness testimony and pointed suspects."""
    testimony_text: str = Field(..., max_length=255)
    pointed_suspects: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_pointed_suspects(self) -> WitnessTestimonyCreateRequest:
        suspect_ids = self.pointed_suspects
        if any(person_id <= 0 for person_id in suspect_ids):
            raise ValueError("All pointed_suspects values must be positive integers.")
        if len(set(suspect_ids)) != len(suspect_ids):
            raise ValueError("pointed_suspects contains duplicate person ids.")
        return self


class TestimonyRead(SchemaModel):
    """Response: Witness testimony details."""
    testimony_id: int = Field(..., gt=0)
    witness_id: int = Field(..., gt=0)
    case_id: int = Field(..., gt=0)
    testimony_text: str = Field(..., max_length=255)
    pointed_suspects: list[int] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


#----------------Suspect Schemas----------------
class CaseSuspectCreateRequest(PersonReferenceInput):
    """Input: Request to add suspect with reason and linked evidence."""
    reason: str | None = Field(default=None, max_length=255)
    evidence_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_ids(self) -> CaseSuspectCreateRequest:
        if any(evidence_id <= 0 for evidence_id in self.evidence_ids):
            raise ValueError("All evidence_ids values must be positive integers.")
        return self


class SuspectRead(SchemaModel):
    """Response: Suspect details including arrest status and linked evidence."""
    suspect_id: int = Field(..., gt=0, description="Person id used as suspect primary key.")
    person: PersonSummary | None = None
    physical_description: str | None = Field(default=None, max_length=255)
    family_contact: str | None = Field(default=None, max_length=15)
    arrest_status: SuspectStatus | None = None
    reason: str | None = Field(default=None, max_length=255)
    linked_evidence_ids: list[int] = Field(default_factory=list)


class SuspectEvidence(SchemaModel):
    """Link between suspect and evidence."""
    suspect_id: int = Field(..., gt=0)
    evidence_id: int = Field(..., gt=0)


class CaseSuspectCreateResponse(SchemaModel):
    """Response: Newly added suspect with assigned ID and details."""
    suspect_id: int = Field(..., gt=0)
    suspect: SuspectRead


class CaseSuspectListRequest(SchemaModel):
    """Input: Request parameters to filter and paginate suspect listings."""
    query: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)


class CaseSuspectListResponse(SchemaModel):
    """Response: List of all suspects in a case."""
    case_id: int = Field(..., gt=0)
    open_date: date
    items: list[SuspectRead] = Field(default_factory=list)


class CaseSuspectUpdateRequest(SchemaModel):
    """Input: Request to update suspect arrest status and bail information."""
    arrest_status: SuspectStatus | None = None
    physical_description: str | None = Field(default=None, max_length=255)
    family_contact: str | None = Field(default=None, max_length=15)
    bail_amount: int | None = Field(default=None, ge=0)
    bail_note: str | None = Field(default=None, max_length=255)


class CaseSuspectUpdateResponse(SchemaModel):
    """Response: Updated suspect confirmation with new details."""
    suspect_id: int = Field(..., gt=0)
    suspect: SuspectRead


#----------------Victim Schemas----------------
class CaseVictimCreateRequest(PersonReferenceInput):
    """Input: Request to add victim to case with harm and contact details."""
    harm_details: str | None = Field(default=None, max_length=255)
    family_contact: str | None = Field(default=None, max_length=15)


class VictimRead(SchemaModel):
    """Response: Victim information including harm details and contact."""
    victim_id: int = Field(..., gt=0, description="Person id used as victim primary key.")
    person: PersonSummary | None = None
    harm_details: str | None = Field(default=None, max_length=255)
    family_contact: str | None = Field(default=None, max_length=15)


class CaseVictimCreateResponse(SchemaModel):
    """Response: Newly added victim with assigned ID and details."""
    victim_id: int = Field(..., gt=0)
    victim: VictimRead


class CaseVictimListResponse(SchemaModel):
    """Response: List of all victims in a case."""
    case_id: int = Field(..., gt=0)
    open_date: date
    items: list[VictimRead] = Field(default_factory=list)


class VictimListQuery(SchemaModel):
    """Input: Query parameters to filter and paginate victim listings."""
    query: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)


#----------------Trial Schemas----------------
class TrialRead(SchemaModel):
    """Response: Trial details including judge, hearing date, and court level."""
    case_id: int = Field(..., gt=0)
    open_date: date
    trial_number: int = Field(..., gt=0)
    trial_id: int = Field(..., gt=0, description="API alias for trial_number.")
    hearing_date: date | None = Field(default=None, description="Maps to trial.hearing.")
    judge_id: int | None = Field(default=None, gt=0)
    court_level: str | None = Field(default=None, max_length=50)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    


class CaseTrialListQuery(SchemaModel):
    """Input: Query parameters to filter trials by open date."""
    open_date: date | None = None


class CaseTrialListResponse(SchemaModel):
    """Response: List of all trials for a case."""
    case_id: int = Field(..., gt=0)
    items: list[TrialRead] = Field(default_factory=list)


class TrialCreateRequest(SchemaModel):
    """Input: Request to create new trial with judge and hearing details."""
    court_id: int | None = Field(
        default=None,
        gt=0,
        description="Not stored in current schema; kept for endpoint compatibility.",
    )
    judge_id: int | None = Field(default=None, gt=0)
    hearing_date: date | None = None
    court_level: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=255)


class TrialCreateResponse(SchemaModel):
    """Response: Newly created trial with assigned ID and details."""
    trial_id: int = Field(..., gt=0)
    trial: TrialRead


class TrialHearingCreateRequest(SchemaModel):
    """Input: Request to record hearing outcome and notes for a trial."""
    hearing_notes: str | None = Field(default=None, max_length=255)
    outcome: str | None = Field(default=None, max_length=255)
    recorded_at: datetime | None = None
    recorded_by: int | None = Field(default=None, gt=0)


class TrialHearingCreateResponse(SchemaModel):
    """Response: Trial confirmation after hearing recorded."""
    trial_id: int = Field(..., gt=0)
    trial: TrialRead


class TrialPunishmentCreateRequest(SchemaModel):
    """Input: Request to assign punishment including fine, jail, or death penalty."""
    person_ids: list[int] = Field(..., min_length=1)
    punishment_type: str | None = Field(
        default=None,
        max_length=50,
        description="Not stored in current schema; can be derived from business rules.",
    )
    fine: int | None = Field(default=None, ge=0)
    jail_start: date | None = None
    jail_end: date | None = None
    death_penalty: str | None = Field(default=None, min_length=1, max_length=1)
    details: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_punishment(self) -> TrialPunishmentCreateRequest:
        if any(person_id <= 0 for person_id in self.person_ids):
            raise ValueError("All person_ids values must be positive integers.")
        if self.jail_start and self.jail_end and self.jail_start > self.jail_end:
            raise ValueError("jail_start cannot be later than jail_end.")
        return self


class PunishmentRead(SchemaModel):
    """Response: Punishment details with fine, jail dates, and penalties."""
    criminal_person_id: int = Field(..., gt=0, description="Maps to punishment.c_personid.")
    case_id: int = Field(..., gt=0)
    open_date: date
    fine: int | None = Field(default=None, ge=0)
    jail_start_date: date | None = None
    jail_end_date: date | None = None
    death_penalty: str | None = Field(default=None, min_length=1, max_length=1)
    punishment_type: str | None = Field(default=None, max_length=50)
    details: str | None = Field(default=None, max_length=255)


class TrialPunishmentCreateResponse(SchemaModel):
    """Response: Assigned punishments for multiple individuals."""
    trial_id: int = Field(..., gt=0)
    punishments: list[PunishmentRead] = Field(default_factory=list)


class TrialDetailResponse(SchemaModel):
    """Response: Complete trial with all associated punishments."""
    trial: TrialRead
    punishments: list[PunishmentRead] = Field(default_factory=list)


class CaseEvidenceWitnessSuspectResponse(SchemaModel):
    """Response: Case with evidence, witnesses, and suspects."""
    case_id: int = Field(..., gt=0)
    open_date: date
    evidence: list[EvidenceRead] = Field(default_factory=list)
    witnesses: list[WitnessRead] = Field(default_factory=list)
    suspects: list[SuspectRead] = Field(default_factory=list)


class CrimeHotspotQuery(SchemaModel):
    """Input: Query parameters to find crime hotspots by city and date range."""
    city: str | None = Field(default=None, max_length=100)
    from_date: date | None = Field(default=None, alias="from")
    to_date: date | None = Field(default=None, alias="to")

    @model_validator(mode="after")
    def validate_date_range(self) -> CrimeHotspotQuery:
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date cannot be later than to_date.")
        return self


class CrimeHotspotItem(SchemaModel):
    """Response: Crime statistics for a city location."""
    city: str = Field(..., max_length=100)
    case_count: int = Field(..., ge=0)


class CrimeHotspotResponse(SchemaModel):
    """Response: List of crime hotspots with case counts."""
    items: list[CrimeHotspotItem] = Field(default_factory=list)


class AuthRole(str, Enum):
    """Enumeration of user roles for RBAC."""
    ADMIN = "admin"
    OFFICER = "officer"
    INVESTIGATOR = "investigator"
    PROSECUTOR = "prosecutor"
    ANALYST = "analyst"
    VIEWER = "viewer"


class PermissionScope(str, Enum):
    """Enumeration of permission scopes for fine-grained access control."""
    # ── Address ───────────────────────────────────────────────
    ADDRESS_READ    = "address:read"
    ADDRESS_WRITE   = "address:write"

    # ── Person ────────────────────────────────────────────────
    PERSON_READ     = "person:read"
    PERSON_WRITE    = "person:write"

    # ── Case ──────────────────────────────────────────────────
    CASE_READ       = "case:read"
    CASE_OPEN       = "case:open"       # create + update
    CASE_CLOSE      = "case:close"

    # ── Officer assignment ────────────────────────────────────
    OFFICER_ASSIGN  = "officer:assign"  # POST /cases/{id}/officers/{oid}
    OFFICER_UNLINK  = "officer:unlink"  # DELETE /cases/{id}/officers/{oid}

    # ── Evidence ──────────────────────────────────────────────
    EVIDENCE_READ   = "evidence:read"
    EVIDENCE_WRITE  = "evidence:write"  # add + update

    # ── Witnesses & Testimony ─────────────────────────────────
    WITNESS_READ    = "witness:read"
    WITNESS_WRITE   = "witness:write"   # add witness + record testimony

    # ── Suspects ──────────────────────────────────────────────
    SUSPECT_READ    = "suspect:read"
    SUSPECT_WRITE   = "suspect:write"   # add + update arrest status

    # ── Victims ───────────────────────────────────────────────
    VICTIM_READ     = "victim:read"
    VICTIM_WRITE    = "victim:write"    # add victim to case

    # ── Trials, Hearings, Punishments ─────────────────────────
    TRIAL_READ      = "trial:read"
    TRIAL_WRITE     = "trial:write"     # create trial + record hearing
    PUNISHMENT_WRITE = "punishment:write"
    JUDGE_ASSIGN    = "judge:assign"    # POST /trials/{id}/judge/{jid}

    # ── Analytics & Snapshot ──────────────────────────────────
    ANALYTICS_READ  = "analytics:read"


class LoginRequest(SchemaModel):
    """Input: User credentials for authentication."""
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1, max_length=200)


class TokenResponse(SchemaModel):
    """Response: Generated access token with roles and scopes."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    person_id: int | None = Field(default=None, gt=0)
    roles: list[AuthRole] = Field(default_factory=list)
    scopes: list[PermissionScope] = Field(default_factory=list)


class RBACAccessCheckRequest(SchemaModel):
    """Input: Request to verify access for endpoint with roles and scopes."""
    endpoint: str = Field(..., min_length=1, max_length=255)
    method: str = Field(..., min_length=3, max_length=10)
    roles: list[AuthRole] = Field(default_factory=list)
    scopes: list[PermissionScope] = Field(default_factory=list)


class RBACAccessCheckResponse(SchemaModel):
    """Response: Access check result with required scopes and reason."""
    allowed: bool
    required_scopes: list[PermissionScope] = Field(default_factory=list)
    reason: str | None = None


__all__ = [
    "CaseStatus",
    "CaseInclude",
    "SuspectStatus",
    "CaseSortBy",
    "CaseKey",
    "PersonReferenceInput",
    "TrialKey",
    "CaseOpenRequest",
    "CaseOpenResponse",
    "CaseUpdateRequest",
    "CaseCloseRequest",
    "CaseCloseResponse",
    "CaseRead",
    "CaseDetailResponse",
    "CaseOfficer",
    "CaseListQuery",
    "CaseListItem",
    "CaseListResponse",
    "CaseEvidenceCreateRequest",
    "CaseEvidenceCreateResponse",
    "CaseEvidenceListResponse",
    "EvidenceRead",
    "CaseWitnessCreateRequest",
    "CaseWitnessCreateResponse",
    "CaseWitnessListResponse",
    "WitnessRead",
    "WitnessTestimonyCreateRequest",
    "TestimonyRead",
    "CaseSuspectCreateRequest",
    "CaseSuspectCreateResponse",
    "CaseSuspectListRequest",
    "CaseSuspectListResponse",
    "CaseSuspectUpdateRequest",
    "CaseSuspectUpdateResponse",
    "SuspectRead",
    "SuspectEvidence",
    "CaseVictimCreateRequest",
    "CaseVictimCreateResponse",
    "CaseVictimListResponse",
    "VictimListQuery",
    "VictimRead",
    "CaseTrialListQuery",
    "CaseTrialListResponse",
    "TrialCreateRequest",
    "TrialCreateResponse",
    "TrialHearingCreateRequest",
    "TrialHearingCreateResponse",
    "TrialPunishmentCreateRequest",
    "TrialPunishmentCreateResponse",
    "TrialDetailResponse",
    "TrialRead",
    "PunishmentRead",
    "CaseEvidenceWitnessSuspectResponse",
    "CrimeHotspotQuery",
    "CrimeHotspotItem",
    "CrimeHotspotResponse",
    "AuthRole",
    "PermissionScope",
    "LoginRequest",
    "TokenResponse",
    "RBACAccessCheckRequest",
    "RBACAccessCheckResponse",
]
