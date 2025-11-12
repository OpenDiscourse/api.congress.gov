"""
Pydantic models for Congress.gov API data structures.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Action(BaseModel):
    """Model for legislative actions."""
    action_date: Optional[str] = Field(None, alias="actionDate")
    text: Optional[str] = None
    type: Optional[str] = None
    action_code: Optional[str] = Field(None, alias="actionCode")
    source_system: Optional[Dict[str, Any]] = Field(None, alias="sourceSystem")
    committees: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(populate_by_name=True)


class Sponsor(BaseModel):
    """Model for bill sponsors."""
    bioguide_id: Optional[str] = Field(None, alias="bioguideId")
    full_name: Optional[str] = Field(None, alias="fullName")
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    party: Optional[str] = None
    state: Optional[str] = None
    district: Optional[int] = None
    is_by_request: Optional[str] = Field(None, alias="isByRequest")

    model_config = ConfigDict(populate_by_name=True)


class Committee(BaseModel):
    """Model for committees."""
    system_code: str = Field(alias="systemCode")
    name: str
    chamber: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    activities: Optional[List[Dict[str, Any]]] = None
    subcommittees: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(populate_by_name=True)


class Bill(BaseModel):
    """Model for bills."""
    congress: int
    bill_type: str = Field(alias="type")
    bill_number: int = Field(alias="number")
    title: Optional[str] = None
    origin_chamber: Optional[str] = Field(None, alias="originChamber")
    origin_chamber_code: Optional[str] = Field(None, alias="originChamberCode")
    update_date: Optional[str] = Field(None, alias="updateDate")
    update_date_including_text: Optional[str] = Field(None, alias="updateDateIncludingText")
    introduced_date: Optional[str] = Field(None, alias="introducedDate")
    constitution_authority_statement_text: Optional[str] = Field(
        None, alias="constitutionAuthorityStatementText"
    )
    policy_area: Optional[Dict[str, Any]] = Field(None, alias="policyArea")
    subjects: Optional[Dict[str, Any]] = None
    latest_action: Optional[Dict[str, Any]] = Field(None, alias="latestAction")
    sponsors: Optional[List[Sponsor]] = None
    cosponsors: Optional[List[Sponsor]] = None
    cosponsors_count: Optional[int] = Field(0, alias="cosponsorsCount")
    committees: Optional[List[Committee]] = None
    related_bills: Optional[List[Dict[str, Any]]] = Field(None, alias="relatedBills")
    actions: Optional[List[Action]] = None
    summaries: Optional[List[Dict[str, Any]]] = None
    amendments: Optional[List[Dict[str, Any]]] = None
    texts: Optional[List[Dict[str, Any]]] = None
    titles: Optional[List[Dict[str, Any]]] = None
    laws: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Member(BaseModel):
    """Model for members of Congress."""
    bioguide_id: str = Field(alias="bioguideId")
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    suffix: Optional[str] = None
    nickname: Optional[str] = None
    party: Optional[str] = None
    state: Optional[str] = None
    district: Optional[int] = None
    birth_year: Optional[int] = Field(None, alias="birthYear")
    death_year: Optional[int] = Field(None, alias="deathYear")
    terms: Optional[List[Dict[str, Any]]] = None
    sponsored_legislation: Optional[Dict[str, Any]] = Field(None, alias="sponsoredLegislation")
    cosponsored_legislation: Optional[Dict[str, Any]] = Field(None, alias="cosponsoredLegislation")
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Amendment(BaseModel):
    """Model for amendments."""
    congress: int
    amendment_type: str = Field(alias="type")
    amendment_number: int = Field(alias="number")
    purpose: Optional[str] = None
    description: Optional[str] = None
    chamber: Optional[str] = None
    latest_action: Optional[Dict[str, Any]] = Field(None, alias="latestAction")
    sponsors: Optional[List[Sponsor]] = None
    cosponsors: Optional[List[Sponsor]] = None
    proposed_date: Optional[str] = Field(None, alias="proposedDate")
    submitted_date: Optional[str] = Field(None, alias="submittedDate")
    actions: Optional[List[Action]] = None
    amendment_to_amendment: Optional[Dict[str, Any]] = Field(None, alias="amendedAmendment")
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Nomination(BaseModel):
    """Model for nominations."""
    congress: int
    nomination_number: str = Field(alias="number")
    part_number: Optional[str] = Field(None, alias="partNumber")
    citation: Optional[str] = None
    description: Optional[str] = None
    received_date: Optional[str] = Field(None, alias="receivedDate")
    authority_date: Optional[str] = Field(None, alias="authorityDate")
    executive_calendar_number: Optional[str] = Field(None, alias="executiveCalendarNumber")
    organization: Optional[str] = None
    position_title: Optional[str] = Field(None, alias="positionTitle")
    latest_action: Optional[Dict[str, Any]] = Field(None, alias="latestAction")
    actions: Optional[List[Action]] = None
    committees: Optional[List[Committee]] = None
    hearings: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Treaty(BaseModel):
    """Model for treaties."""
    congress: int
    treaty_number: int = Field(alias="number")
    suffix: Optional[str] = None
    treaty_name: Optional[str] = Field(None, alias="topic")
    topic: Optional[str] = None
    country: Optional[str] = None
    transmitted_date: Optional[str] = Field(None, alias="transmittedDate")
    in_force_date: Optional[str] = Field(None, alias="inForceDate")
    resolution_text: Optional[str] = Field(None, alias="resolutionText")
    latest_action: Optional[Dict[str, Any]] = Field(None, alias="latestAction")
    actions: Optional[List[Action]] = None
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CommitteeReport(BaseModel):
    """Model for committee reports."""
    congress: int
    report_type: str = Field(alias="type")
    report_number: int = Field(alias="number")
    part: Optional[int] = None
    citation: Optional[str] = None
    title: Optional[str] = None
    chamber: Optional[str] = None
    report_date: Optional[str] = Field(None, alias="updateDate")
    committees: Optional[List[Committee]] = None
    associated_bills: Optional[List[Dict[str, Any]]] = Field(None, alias="associatedBills")
    associated_treaties: Optional[List[Dict[str, Any]]] = Field(None, alias="associatedTreaties")
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class Hearing(BaseModel):
    """Model for hearings."""
    congress: int
    chamber: str
    jacket_number: int = Field(alias="jacketNumber")
    hearing_number: Optional[str] = Field(None, alias="number")
    part: Optional[int] = None
    citation: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = Field(None, alias="updateDate")
    committees: Optional[List[Committee]] = None
    associated_bills: Optional[List[Dict[str, Any]]] = Field(None, alias="associatedBills")
    formats: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CongressionalRecord(BaseModel):
    """Model for Congressional Record."""
    congress: int
    session: int
    issue_number: int = Field(alias="issueNumber")
    volume_number: int = Field(alias="volumeNumber")
    publication_date: Optional[str] = Field(None, alias="publicationDate")
    sections: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class PaginationInfo(BaseModel):
    """Model for API pagination."""
    count: int
    next: Optional[str] = None
    prev: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class APIResponse(BaseModel):
    """Generic model for API responses."""
    request: Optional[Dict[str, Any]] = None
    pagination: Optional[PaginationInfo] = None
    data: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(populate_by_name=True)
