"""
Tests for Pydantic models.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
import pytest
from datetime import datetime
from models import Bill, Member, Amendment, Committee, Sponsor


def test_bill_model():
    """Test Bill model validation."""
    bill_data = {
        'congress': 118,
        'type': 'hr',
        'number': 1234,
        'title': 'Test Bill',
        'originChamber': 'House'
    }
    
    bill = Bill(**bill_data)
    assert bill.congress == 118
    assert bill.bill_type == 'hr'
    assert bill.bill_number == 1234
    assert bill.title == 'Test Bill'
    assert bill.origin_chamber == 'House'


def test_member_model():
    """Test Member model validation."""
    member_data = {
        'bioguideId': 'B000944',
        'firstName': 'Sherrod',
        'lastName': 'Brown',
        'party': 'D',
        'state': 'OH'
    }
    
    member = Member(**member_data)
    assert member.bioguide_id == 'B000944'
    assert member.first_name == 'Sherrod'
    assert member.last_name == 'Brown'
    assert member.party == 'D'
    assert member.state == 'OH'


def test_sponsor_model():
    """Test Sponsor model validation."""
    sponsor_data = {
        'bioguideId': 'B000944',
        'fullName': 'Sen. Brown, Sherrod [D-OH]',
        'firstName': 'Sherrod',
        'lastName': 'Brown',
        'party': 'D',
        'state': 'OH'
    }
    
    sponsor = Sponsor(**sponsor_data)
    assert sponsor.bioguide_id == 'B000944'
    assert sponsor.full_name == 'Sen. Brown, Sherrod [D-OH]'
    assert sponsor.party == 'D'


def test_committee_model():
    """Test Committee model validation."""
    committee_data = {
        'systemCode': 'hsgo00',
        'name': 'House Committee on Oversight and Reform',
        'chamber': 'House',
        'type': 'Standing'
    }
    
    committee = Committee(**committee_data)
    assert committee.system_code == 'hsgo00'
    assert committee.name == 'House Committee on Oversight and Reform'
    assert committee.chamber == 'House'
    assert committee.type == 'Standing'


def test_amendment_model():
    """Test Amendment model validation."""
    amendment_data = {
        'congress': 118,
        'type': 'hamdt',
        'number': 123,
        'purpose': 'To amend the bill',
        'chamber': 'House'
    }
    
    amendment = Amendment(**amendment_data)
    assert amendment.congress == 118
    assert amendment.amendment_type == 'hamdt'
    assert amendment.amendment_number == 123
    assert amendment.purpose == 'To amend the bill'
    assert amendment.chamber == 'House'


def test_bill_with_nested_data():
    """Test Bill model with nested sponsor data."""
    bill_data = {
        'congress': 118,
        'type': 'hr',
        'number': 1234,
        'title': 'Test Bill',
        'sponsors': [
            {
                'bioguideId': 'B000944',
                'fullName': 'Sen. Brown, Sherrod [D-OH]',
                'party': 'D'
            }
        ],
        'cosponsorsCount': 25
    }
    
    bill = Bill(**bill_data)
    assert bill.congress == 118
    assert bill.sponsors is not None
    assert len(bill.sponsors) == 1
    assert bill.sponsors[0].bioguide_id == 'B000944'
    assert bill.cosponsors_count == 25
