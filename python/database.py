"""
Database interaction layer for Congress.gov API data.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import json
import os

from sqlalchemy import (
    create_engine, text, Column, Integer, String, Date, 
    Boolean, Text, TIMESTAMP, JSON, and_, or_
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool

from models import Bill, Member, Amendment, Committee


Base = declarative_base()


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            connection_string: PostgreSQL connection string.
                              If None, reads from DATABASE_URL environment variable.
        """
        if connection_string is None:
            connection_string = os.getenv(
                'DATABASE_URL',
                'postgresql://congress_user:congress_pass@localhost:5432/congress_api'
            )
        
        self.engine = create_engine(
            connection_string,
            poolclass=NullPool,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute raw SQL query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        with self.get_session() as session:
            result = session.execute(text(sql), params or {})
            if result.returns_rows:
                return [dict(row._mapping) for row in result]
            return []

    def insert_bill(self, bill_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert or update a bill in the database.
        
        Args:
            bill_data: Bill data dictionary
            
        Returns:
            Bill ID if successful, None otherwise
        """
        sql = """
        INSERT INTO bills (
            congress, bill_type, bill_number, title, origin_chamber,
            origin_chamber_code, update_date, update_date_including_text,
            introduced_date, constitution_authority_statement_text,
            policy_area, subjects, latest_action, sponsors,
            cosponsors_count, committees, related_bills, actions,
            summaries, amendments, texts, titles, law_number,
            law_type, is_law, raw_data
        ) VALUES (
            :congress, :bill_type, :bill_number, :title, :origin_chamber,
            :origin_chamber_code, :update_date, :update_date_including_text,
            :introduced_date, :constitution_authority_statement_text,
            :policy_area, :subjects, :latest_action, :sponsors,
            :cosponsors_count, :committees, :related_bills, :actions,
            :summaries, :amendments, :texts, :titles, :law_number,
            :law_type, :is_law, :raw_data
        )
        ON CONFLICT (congress, bill_type, bill_number)
        DO UPDATE SET
            title = EXCLUDED.title,
            update_date = EXCLUDED.update_date,
            update_date_including_text = EXCLUDED.update_date_including_text,
            latest_action = EXCLUDED.latest_action,
            cosponsors_count = EXCLUDED.cosponsors_count,
            actions = EXCLUDED.actions,
            summaries = EXCLUDED.summaries,
            amendments = EXCLUDED.amendments,
            texts = EXCLUDED.texts,
            titles = EXCLUDED.titles,
            is_law = EXCLUDED.is_law,
            law_number = EXCLUDED.law_number,
            law_type = EXCLUDED.law_type,
            raw_data = EXCLUDED.raw_data,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        # Prepare data
        params = {
            'congress': bill_data.get('congress'),
            'bill_type': bill_data.get('type'),
            'bill_number': bill_data.get('number'),
            'title': bill_data.get('title'),
            'origin_chamber': bill_data.get('originChamber'),
            'origin_chamber_code': bill_data.get('originChamberCode'),
            'update_date': bill_data.get('updateDate'),
            'update_date_including_text': bill_data.get('updateDateIncludingText'),
            'introduced_date': bill_data.get('introducedDate'),
            'constitution_authority_statement_text': bill_data.get('constitutionAuthorityStatementText'),
            'policy_area': json.dumps(bill_data.get('policyArea')) if bill_data.get('policyArea') else None,
            'subjects': json.dumps(bill_data.get('subjects')) if bill_data.get('subjects') else None,
            'latest_action': json.dumps(bill_data.get('latestAction')) if bill_data.get('latestAction') else None,
            'sponsors': json.dumps(bill_data.get('sponsors', [])),
            'cosponsors_count': bill_data.get('cosponsorsCount', 0),
            'committees': json.dumps(bill_data.get('committees', [])),
            'related_bills': json.dumps(bill_data.get('relatedBills', [])),
            'actions': json.dumps(bill_data.get('actions', [])),
            'summaries': json.dumps(bill_data.get('summaries', [])),
            'amendments': json.dumps(bill_data.get('amendments', [])),
            'texts': json.dumps(bill_data.get('texts', [])),
            'titles': json.dumps(bill_data.get('titles', [])),
            'law_number': bill_data.get('laws', [{}])[0].get('number') if bill_data.get('laws') else None,
            'law_type': bill_data.get('laws', [{}])[0].get('type') if bill_data.get('laws') else None,
            'is_law': bool(bill_data.get('laws')),
            'raw_data': json.dumps(bill_data)
        }
        
        try:
            result = self.execute_sql(sql, params)
            return result[0]['id'] if result else None
        except Exception as e:
            print(f"Error inserting bill: {e}")
            return None

    def insert_member(self, member_data: Dict[str, Any]) -> Optional[int]:
        """Insert or update a member in the database."""
        sql = """
        INSERT INTO members (
            bioguide_id, first_name, last_name, middle_name,
            suffix, nickname, party, state, district,
            birth_year, death_year, terms
        ) VALUES (
            :bioguide_id, :first_name, :last_name, :middle_name,
            :suffix, :nickname, :party, :state, :district,
            :birth_year, :death_year, :terms
        )
        ON CONFLICT (bioguide_id)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            party = EXCLUDED.party,
            state = EXCLUDED.state,
            district = EXCLUDED.district,
            terms = EXCLUDED.terms,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        params = {
            'bioguide_id': member_data.get('bioguideId'),
            'first_name': member_data.get('firstName'),
            'last_name': member_data.get('lastName'),
            'middle_name': member_data.get('middleName'),
            'suffix': member_data.get('suffix'),
            'nickname': member_data.get('nickname'),
            'party': member_data.get('party'),
            'state': member_data.get('state'),
            'district': member_data.get('district'),
            'birth_year': member_data.get('birthYear'),
            'death_year': member_data.get('deathYear'),
            'terms': json.dumps(member_data.get('terms', []))
        }
        
        try:
            result = self.execute_sql(sql, params)
            return result[0]['id'] if result else None
        except Exception as e:
            print(f"Error inserting member: {e}")
            return None

    def insert_amendment(self, amendment_data: Dict[str, Any]) -> Optional[int]:
        """Insert or update an amendment in the database."""
        sql = """
        INSERT INTO amendments (
            congress, amendment_type, amendment_number, bill_congress,
            bill_type, bill_number, purpose, description, chamber,
            amendment_to_amendment, sponsors, cosponsors, proposed_date,
            submitted_date, latest_action, actions, raw_data
        ) VALUES (
            :congress, :amendment_type, :amendment_number, :bill_congress,
            :bill_type, :bill_number, :purpose, :description, :chamber,
            :amendment_to_amendment, :sponsors, :cosponsors, :proposed_date,
            :submitted_date, :latest_action, :actions, :raw_data
        )
        ON CONFLICT (congress, amendment_type, amendment_number)
        DO UPDATE SET
            purpose = EXCLUDED.purpose,
            description = EXCLUDED.description,
            latest_action = EXCLUDED.latest_action,
            actions = EXCLUDED.actions,
            raw_data = EXCLUDED.raw_data,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        params = {
            'congress': amendment_data.get('congress'),
            'amendment_type': amendment_data.get('type'),
            'amendment_number': amendment_data.get('number'),
            'bill_congress': amendment_data.get('amendedBill', {}).get('congress'),
            'bill_type': amendment_data.get('amendedBill', {}).get('type'),
            'bill_number': amendment_data.get('amendedBill', {}).get('number'),
            'purpose': amendment_data.get('purpose'),
            'description': amendment_data.get('description'),
            'chamber': amendment_data.get('chamber'),
            'amendment_to_amendment': json.dumps(amendment_data.get('amendedAmendment')) if amendment_data.get('amendedAmendment') else None,
            'sponsors': json.dumps(amendment_data.get('sponsors', [])),
            'cosponsors': json.dumps(amendment_data.get('cosponsors', [])),
            'proposed_date': amendment_data.get('proposedDate'),
            'submitted_date': amendment_data.get('submittedDate'),
            'latest_action': json.dumps(amendment_data.get('latestAction')) if amendment_data.get('latestAction') else None,
            'actions': json.dumps(amendment_data.get('actions', [])),
            'raw_data': json.dumps(amendment_data)
        }
        
        try:
            result = self.execute_sql(sql, params)
            return result[0]['id'] if result else None
        except Exception as e:
            print(f"Error inserting amendment: {e}")
            return None

    def insert_committee(self, committee_data: Dict[str, Any]) -> Optional[int]:
        """Insert or update a committee in the database."""
        sql = """
        INSERT INTO committees (
            system_code, name, chamber, type, subcommittees,
            parent_committee_system_code, is_subcommittee
        ) VALUES (
            :system_code, :name, :chamber, :type, :subcommittees,
            :parent_committee_system_code, :is_subcommittee
        )
        ON CONFLICT (system_code)
        DO UPDATE SET
            name = EXCLUDED.name,
            chamber = EXCLUDED.chamber,
            type = EXCLUDED.type,
            subcommittees = EXCLUDED.subcommittees,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        params = {
            'system_code': committee_data.get('systemCode'),
            'name': committee_data.get('name'),
            'chamber': committee_data.get('chamber'),
            'type': committee_data.get('type'),
            'subcommittees': json.dumps(committee_data.get('subcommittees', [])),
            'parent_committee_system_code': committee_data.get('parentCommitteeCode'),
            'is_subcommittee': committee_data.get('isCurrent', False)
        }
        
        try:
            result = self.execute_sql(sql, params)
            return result[0]['id'] if result else None
        except Exception as e:
            print(f"Error inserting committee: {e}")
            return None

    def log_sync(
        self,
        endpoint: str,
        sync_type: str,
        status: str = 'running',
        records_processed: int = 0,
        records_created: int = 0,
        records_updated: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log API sync operation."""
        sql = """
        INSERT INTO api_sync_log (
            endpoint, sync_type, started_at, status, records_processed,
            records_created, records_updated, records_failed, error_message, parameters
        ) VALUES (
            :endpoint, :sync_type, :started_at, :status, :records_processed,
            :records_created, :records_updated, :records_failed, :error_message, :parameters
        )
        RETURNING id
        """
        
        params = {
            'endpoint': endpoint,
            'sync_type': sync_type,
            'started_at': datetime.now(),
            'status': status,
            'records_processed': records_processed,
            'records_created': records_created,
            'records_updated': records_updated,
            'records_failed': records_failed,
            'error_message': error_message,
            'parameters': json.dumps(parameters) if parameters else None
        }
        
        result = self.execute_sql(sql, params)
        return result[0]['id'] if result else None

    def update_sync_log(
        self,
        log_id: int,
        status: str,
        records_processed: int = 0,
        records_created: int = 0,
        records_updated: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None
    ):
        """Update API sync log."""
        sql = """
        UPDATE api_sync_log
        SET status = :status,
            completed_at = :completed_at,
            records_processed = :records_processed,
            records_created = :records_created,
            records_updated = :records_updated,
            records_failed = :records_failed,
            error_message = :error_message
        WHERE id = :log_id
        """
        
        params = {
            'log_id': log_id,
            'status': status,
            'completed_at': datetime.now(),
            'records_processed': records_processed,
            'records_created': records_created,
            'records_updated': records_updated,
            'records_failed': records_failed,
            'error_message': error_message
        }
        
        self.execute_sql(sql, params)

    def get_bills(
        self,
        congress: Optional[int] = None,
        bill_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve bills with optional filters."""
        conditions = []
        params = {'limit': limit, 'offset': offset}
        
        if congress:
            conditions.append("congress = :congress")
            params['congress'] = congress
        if bill_type:
            conditions.append("bill_type = :bill_type")
            params['bill_type'] = bill_type
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
        SELECT * FROM bills
        {where_clause}
        ORDER BY update_date DESC
        LIMIT :limit OFFSET :offset
        """
        
        return self.execute_sql(sql, params)

    def search_bills(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search bills by keyword in title."""
        sql = """
        SELECT * FROM search_bills(:keyword)
        LIMIT :limit
        """
        return self.execute_sql(sql, {'keyword': keyword, 'limit': limit})

    def get_member_statistics(self, bioguide_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific member."""
        sql = "SELECT * FROM get_member_statistics(:bioguide_id)"
        result = self.execute_sql(sql, {'bioguide_id': bioguide_id})
        return result[0] if result else None

    def get_session_statistics(self, congress: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get session statistics."""
        if congress:
            sql = "SELECT * FROM session_statistics WHERE congress = :congress"
            return self.execute_sql(sql, {'congress': congress})
        else:
            sql = "SELECT * FROM session_statistics ORDER BY congress DESC LIMIT 10"
            return self.execute_sql(sql)
