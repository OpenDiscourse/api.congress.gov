"""
Bulk data ingestion module for Congress.gov API.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
import time
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
import logging

from tqdm import tqdm
from cdg_client import CDGClient
from database import DatabaseManager
from models import Bill, Member, Amendment, Committee


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BulkIngestor:
    """Handles bulk data ingestion from Congress.gov API."""

    def __init__(
        self,
        api_key: str,
        db_manager: DatabaseManager,
        rate_limit_delay: float = 0.75  # ~4800 requests per hour
    ):
        """
        Initialize bulk ingestor.
        
        Args:
            api_key: Congress.gov API key
            db_manager: Database manager instance
            rate_limit_delay: Delay between API requests in seconds
        """
        self.client = CDGClient(api_key, response_format='json')
        self.db = db_manager
        self.rate_limit_delay = rate_limit_delay
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        time.sleep(self.rate_limit_delay)

    def _fetch_paginated(
        self,
        endpoint: str,
        limit: int = 250,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all pages from a paginated endpoint.
        
        Args:
            endpoint: API endpoint
            limit: Items per page
            max_pages: Maximum pages to fetch (None for all)
            
        Returns:
            List of all items
        """
        all_items = []
        page = 0
        next_url = f"{endpoint}?limit={limit}&offset=0"
        
        while next_url and (max_pages is None or page < max_pages):
            try:
                self._rate_limit()
                data, status_code = self.client.get(next_url)
                
                if status_code != 200:
                    logger.error(f"Error fetching {next_url}: Status {status_code}")
                    break
                
                # Extract items based on endpoint type
                items = self._extract_items(data)
                all_items.extend(items)
                
                # Get next page URL
                pagination = data.get('pagination', {})
                next_url = pagination.get('next')
                
                page += 1
                logger.info(f"Fetched page {page}, {len(items)} items, total: {len(all_items)}")
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_items

    def _extract_items(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract items from API response."""
        # Try common item keys
        for key in ['bills', 'members', 'amendments', 'committees', 'nominations', 
                    'treaties', 'reports', 'hearings', 'items']:
            if key in data:
                items = data[key]
                return items if isinstance(items, list) else [items]
        return []

    def ingest_bills(
        self,
        congress: Optional[int] = None,
        bill_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Ingest bills from the API.
        
        Args:
            congress: Congress number (e.g., 118)
            bill_type: Bill type (hr, s, hjres, sjres, etc.)
            from_date: Start date (ISO format)
            to_date: End date (ISO format)
            max_pages: Maximum pages to fetch
            
        Returns:
            Statistics dictionary
        """
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}
        
        # Build endpoint
        if congress and bill_type:
            endpoint = f"bill/{congress}/{bill_type}"
        elif congress:
            endpoint = f"bill/{congress}"
        else:
            endpoint = "bill"
        
        # Add date filters
        if from_date or to_date:
            params = []
            if from_date:
                params.append(f"fromDateTime={from_date}")
            if to_date:
                params.append(f"toDateTime={to_date}")
            endpoint += "?" + "&".join(params)
        
        log_id = self.db.log_sync(
            endpoint='bills',
            sync_type='bulk',
            parameters={'congress': congress, 'bill_type': bill_type}
        )
        
        try:
            logger.info(f"Starting bill ingestion: {endpoint}")
            bills = self._fetch_paginated(endpoint, max_pages=max_pages)
            
            logger.info(f"Processing {len(bills)} bills...")
            for bill_data in tqdm(bills, desc="Processing bills"):
                try:
                    # Fetch detailed bill data if needed
                    if 'title' not in bill_data or not bill_data.get('title'):
                        detail_endpoint = bill_data.get('url', '').replace(
                            'https://api.congress.gov/v3/', ''
                        )
                        if detail_endpoint:
                            self._rate_limit()
                            detail_data, _ = self.client.get(detail_endpoint)
                            bill_data = detail_data.get('bill', bill_data)
                    
                    # Insert into database
                    bill_id = self.db.insert_bill(bill_data)
                    if bill_id:
                        self.stats['created'] += 1
                    else:
                        self.stats['updated'] += 1
                    self.stats['processed'] += 1
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    self.stats['errors'].append(str(e))
                    logger.error(f"Error processing bill: {e}")
            
            self.db.update_sync_log(
                log_id,
                status='completed',
                records_processed=self.stats['processed'],
                records_created=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed']
            )
            
        except Exception as e:
            logger.error(f"Fatal error during bill ingestion: {e}")
            self.db.update_sync_log(
                log_id,
                status='failed',
                error_message=str(e)
            )
        
        return self.stats

    def ingest_members(
        self,
        congress: Optional[int] = None,
        max_pages: Optional[int] = None
    ) -> Dict[str, int]:
        """Ingest members from the API."""
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}
        
        endpoint = f"member/congress/{congress}" if congress else "member"
        
        log_id = self.db.log_sync(
            endpoint='members',
            sync_type='bulk',
            parameters={'congress': congress}
        )
        
        try:
            logger.info(f"Starting member ingestion: {endpoint}")
            members = self._fetch_paginated(endpoint, max_pages=max_pages)
            
            logger.info(f"Processing {len(members)} members...")
            for member_data in tqdm(members, desc="Processing members"):
                try:
                    # Fetch detailed member data
                    bioguide_id = member_data.get('bioguideId')
                    if bioguide_id:
                        self._rate_limit()
                        detail_endpoint = f"member/{bioguide_id}"
                        detail_data, _ = self.client.get(detail_endpoint)
                        member_data = detail_data.get('member', member_data)
                    
                    member_id = self.db.insert_member(member_data)
                    if member_id:
                        self.stats['created'] += 1
                    else:
                        self.stats['updated'] += 1
                    self.stats['processed'] += 1
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    self.stats['errors'].append(str(e))
                    logger.error(f"Error processing member: {e}")
            
            self.db.update_sync_log(
                log_id,
                status='completed',
                records_processed=self.stats['processed'],
                records_created=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed']
            )
            
        except Exception as e:
            logger.error(f"Fatal error during member ingestion: {e}")
            self.db.update_sync_log(log_id, status='failed', error_message=str(e))
        
        return self.stats

    def ingest_amendments(
        self,
        congress: Optional[int] = None,
        max_pages: Optional[int] = None
    ) -> Dict[str, int]:
        """Ingest amendments from the API."""
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}
        
        endpoint = f"amendment/{congress}" if congress else "amendment"
        
        log_id = self.db.log_sync(
            endpoint='amendments',
            sync_type='bulk',
            parameters={'congress': congress}
        )
        
        try:
            logger.info(f"Starting amendment ingestion: {endpoint}")
            amendments = self._fetch_paginated(endpoint, max_pages=max_pages)
            
            logger.info(f"Processing {len(amendments)} amendments...")
            for amendment_data in tqdm(amendments, desc="Processing amendments"):
                try:
                    amendment_id = self.db.insert_amendment(amendment_data)
                    if amendment_id:
                        self.stats['created'] += 1
                    else:
                        self.stats['updated'] += 1
                    self.stats['processed'] += 1
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    self.stats['errors'].append(str(e))
                    logger.error(f"Error processing amendment: {e}")
            
            self.db.update_sync_log(
                log_id,
                status='completed',
                records_processed=self.stats['processed'],
                records_created=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed']
            )
            
        except Exception as e:
            logger.error(f"Fatal error during amendment ingestion: {e}")
            self.db.update_sync_log(log_id, status='failed', error_message=str(e))
        
        return self.stats

    def ingest_committees(self, max_pages: Optional[int] = None) -> Dict[str, int]:
        """Ingest committees from the API."""
        self.stats = {'processed': 0, 'created': 0, 'updated': 0, 'failed': 0, 'errors': []}
        
        log_id = self.db.log_sync(endpoint='committees', sync_type='bulk')
        
        try:
            logger.info("Starting committee ingestion")
            
            # Ingest both House and Senate committees
            for chamber in ['house', 'senate']:
                endpoint = f"committee/{chamber}"
                committees = self._fetch_paginated(endpoint, max_pages=max_pages)
                
                logger.info(f"Processing {len(committees)} {chamber} committees...")
                for committee_data in tqdm(committees, desc=f"Processing {chamber} committees"):
                    try:
                        committee_id = self.db.insert_committee(committee_data)
                        if committee_id:
                            self.stats['created'] += 1
                        else:
                            self.stats['updated'] += 1
                        self.stats['processed'] += 1
                        
                    except Exception as e:
                        self.stats['failed'] += 1
                        self.stats['errors'].append(str(e))
                        logger.error(f"Error processing committee: {e}")
            
            self.db.update_sync_log(
                log_id,
                status='completed',
                records_processed=self.stats['processed'],
                records_created=self.stats['created'],
                records_updated=self.stats['updated'],
                records_failed=self.stats['failed']
            )
            
        except Exception as e:
            logger.error(f"Fatal error during committee ingestion: {e}")
            self.db.update_sync_log(log_id, status='failed', error_message=str(e))
        
        return self.stats

    def sync_recent_bills(self, days: int = 7) -> Dict[str, int]:
        """
        Sync bills updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        to_date = datetime.now().isoformat() + 'Z'
        from_date = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        
        logger.info(f"Syncing bills from {from_date} to {to_date}")
        return self.ingest_bills(from_date=from_date, to_date=to_date)
