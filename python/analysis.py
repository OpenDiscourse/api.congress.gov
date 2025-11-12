"""
Analysis and research methods for Congress.gov data using Pydantic AI.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

import pandas as pd
import numpy as np
from scipy import stats

from database import DatabaseManager


class CongressDataAnalyzer:
    """Comprehensive analysis tools for Congressional data."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize analyzer.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    # ==================== Data Query Methods ====================

    def get_bills_dataframe(
        self,
        congress: Optional[int] = None,
        bill_type: Optional[str] = None,
        is_law: Optional[bool] = None,
        limit: int = 10000
    ) -> pd.DataFrame:
        """
        Get bills as a pandas DataFrame for analysis.
        
        Args:
            congress: Filter by congress number
            bill_type: Filter by bill type
            is_law: Filter by law status
            limit: Maximum records to return
            
        Returns:
            DataFrame with bill data
        """
        conditions = []
        params = {'limit': limit}
        
        if congress is not None:
            conditions.append("congress = :congress")
            params['congress'] = congress
        if bill_type is not None:
            conditions.append("bill_type = :bill_type")
            params['bill_type'] = bill_type
        if is_law is not None:
            conditions.append("is_law = :is_law")
            params['is_law'] = is_law
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
        SELECT 
            id, congress, bill_type, bill_number, title,
            origin_chamber, introduced_date, update_date,
            cosponsors_count, is_law, policy_area, subjects,
            latest_action, sponsors, committees, raw_data
        FROM bills
        {where_clause}
        ORDER BY introduced_date DESC
        LIMIT :limit
        """
        
        results = self.db.execute_sql(sql, params)
        df = pd.DataFrame(results)
        
        # Parse JSON columns
        if not df.empty:
            for col in ['policy_area', 'subjects', 'latest_action', 'sponsors', 'committees']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: json.loads(x) if x else None)
        
        return df

    def get_random_sample(
        self,
        table: str,
        sample_size: int = 100,
        conditions: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Get a random sample from a table.
        
        Args:
            table: Table name
            sample_size: Number of records to sample
            conditions: Filter conditions
            
        Returns:
            DataFrame with sampled data
        """
        where_clause = ""
        params = {'sample_size': sample_size}
        
        if conditions:
            clauses = []
            for key, value in conditions.items():
                clauses.append(f"{key} = :{key}")
                params[key] = value
            where_clause = " WHERE " + " AND ".join(clauses)
        
        sql = f"""
        SELECT * FROM {table}
        {where_clause}
        ORDER BY RANDOM()
        LIMIT :sample_size
        """
        
        results = self.db.execute_sql(sql, params)
        return pd.DataFrame(results)

    def query_bills_by_criteria(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        congress_list: Optional[List[int]] = None,
        policy_areas: Optional[List[str]] = None,
        min_cosponsors: Optional[int] = None,
        chambers: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Query bills with multiple criteria.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            congress_list: List of congress numbers
            policy_areas: List of policy areas
            min_cosponsors: Minimum number of cosponsors
            chambers: List of chambers (House, Senate)
            
        Returns:
            DataFrame with matching bills
        """
        conditions = []
        params = {}
        
        if start_date:
            conditions.append("introduced_date >= :start_date")
            params['start_date'] = start_date
        if end_date:
            conditions.append("introduced_date <= :end_date")
            params['end_date'] = end_date
        if congress_list:
            conditions.append("congress = ANY(:congress_list)")
            params['congress_list'] = congress_list
        if min_cosponsors is not None:
            conditions.append("cosponsors_count >= :min_cosponsors")
            params['min_cosponsors'] = min_cosponsors
        if chambers:
            conditions.append("origin_chamber = ANY(:chambers)")
            params['chambers'] = chambers
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
        SELECT * FROM bills
        {where_clause}
        ORDER BY introduced_date DESC
        """
        
        results = self.db.execute_sql(sql, params)
        df = pd.DataFrame(results)
        
        # Filter by policy areas if specified (requires JSON parsing)
        if policy_areas and not df.empty:
            df['policy_area_parsed'] = df['policy_area'].apply(
                lambda x: json.loads(x) if x else None
            )
            df = df[df['policy_area_parsed'].apply(
                lambda x: x and x.get('name') in policy_areas if x else False
            )]
        
        return df

    # ==================== Statistical Analysis Methods ====================

    def calculate_bill_statistics(self, congress: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive bill statistics.
        
        Args:
            congress: Congress number (None for all)
            
        Returns:
            Dictionary with statistics
        """
        df = self.get_bills_dataframe(congress=congress)
        
        if df.empty:
            return {'error': 'No data available'}
        
        stats_dict = {
            'total_bills': len(df),
            'laws_enacted': len(df[df['is_law'] == True]),
            'law_passage_rate': len(df[df['is_law'] == True]) / len(df) if len(df) > 0 else 0,
            'by_chamber': df['origin_chamber'].value_counts().to_dict(),
            'by_type': df['bill_type'].value_counts().to_dict(),
            'cosponsors_stats': {
                'mean': float(df['cosponsors_count'].mean()),
                'median': float(df['cosponsors_count'].median()),
                'std': float(df['cosponsors_count'].std()),
                'max': int(df['cosponsors_count'].max()),
                'min': int(df['cosponsors_count'].min())
            }
        }
        
        return stats_dict

    def temporal_analysis(
        self,
        congress: int,
        grouping: str = 'month'
    ) -> pd.DataFrame:
        """
        Analyze bill introduction trends over time.
        
        Args:
            congress: Congress number
            grouping: Time grouping ('day', 'week', 'month', 'quarter')
            
        Returns:
            DataFrame with temporal trends
        """
        df = self.get_bills_dataframe(congress=congress)
        
        if df.empty:
            return pd.DataFrame()
        
        df['introduced_date'] = pd.to_datetime(df['introduced_date'])
        
        # Group by time period
        if grouping == 'day':
            df['period'] = df['introduced_date'].dt.date
        elif grouping == 'week':
            df['period'] = df['introduced_date'].dt.to_period('W').dt.start_time
        elif grouping == 'month':
            df['period'] = df['introduced_date'].dt.to_period('M').dt.start_time
        elif grouping == 'quarter':
            df['period'] = df['introduced_date'].dt.to_period('Q').dt.start_time
        
        # Aggregate statistics
        temporal_stats = df.groupby('period').agg({
            'id': 'count',
            'is_law': 'sum',
            'cosponsors_count': ['mean', 'median', 'sum']
        }).reset_index()
        
        temporal_stats.columns = [
            'period', 'total_bills', 'laws_enacted',
            'avg_cosponsors', 'median_cosponsors', 'total_cosponsors'
        ]
        
        return temporal_stats

    def policy_area_analysis(self, congress: Optional[int] = None) -> pd.DataFrame:
        """
        Analyze bills by policy area.
        
        Args:
            congress: Congress number (None for all)
            
        Returns:
            DataFrame with policy area statistics
        """
        df = self.get_bills_dataframe(congress=congress)
        
        if df.empty:
            return pd.DataFrame()
        
        # Extract policy areas
        policy_areas = []
        for _, row in df.iterrows():
            if row['policy_area'] and isinstance(row['policy_area'], dict):
                area_name = row['policy_area'].get('name', 'Unknown')
                policy_areas.append({
                    'policy_area': area_name,
                    'is_law': row['is_law'],
                    'cosponsors': row['cosponsors_count']
                })
        
        if not policy_areas:
            return pd.DataFrame()
        
        pa_df = pd.DataFrame(policy_areas)
        
        # Aggregate by policy area
        stats = pa_df.groupby('policy_area').agg({
            'policy_area': 'count',
            'is_law': 'sum',
            'cosponsors': ['mean', 'sum']
        }).reset_index()
        
        stats.columns = ['policy_area', 'total_bills', 'laws_enacted', 'avg_cosponsors', 'total_cosponsors']
        stats = stats.sort_values('total_bills', ascending=False)
        
        return stats

    def bipartisan_analysis(self, congress: int) -> Dict[str, Any]:
        """
        Analyze bipartisan support for bills.
        
        Args:
            congress: Congress number
            
        Returns:
            Dictionary with bipartisan metrics
        """
        sql = """
        SELECT 
            b.id,
            b.title,
            b.is_law,
            b.sponsors,
            b.cosponsors_count,
            b.raw_data->'cosponsors' as cosponsors
        FROM bills b
        WHERE b.congress = :congress
        AND b.cosponsors_count > 0
        """
        
        results = self.db.execute_sql(sql, {'congress': congress})
        df = pd.DataFrame(results)
        
        if df.empty:
            return {'error': 'No data available'}
        
        bipartisan_bills = []
        
        for _, row in df.iterrows():
            sponsors = json.loads(row['sponsors']) if isinstance(row['sponsors'], str) else row['sponsors']
            cosponsors = json.loads(row['cosponsors']) if isinstance(row['cosponsors'], str) else (row['cosponsors'] or [])
            
            if not sponsors or not cosponsors:
                continue
            
            sponsor_party = sponsors[0].get('party', 'Unknown') if sponsors else 'Unknown'
            
            # Count party distribution in cosponsors
            party_counts = Counter([c.get('party', 'Unknown') for c in cosponsors])
            
            # Check if bipartisan (has both D and R)
            is_bipartisan = 'D' in party_counts and 'R' in party_counts
            
            if is_bipartisan:
                bipartisan_bills.append({
                    'id': row['id'],
                    'title': row['title'],
                    'is_law': row['is_law'],
                    'sponsor_party': sponsor_party,
                    'dem_cosponsors': party_counts.get('D', 0),
                    'rep_cosponsors': party_counts.get('R', 0),
                    'total_cosponsors': row['cosponsors_count']
                })
        
        bipartisan_df = pd.DataFrame(bipartisan_bills)
        
        if bipartisan_df.empty:
            return {'bipartisan_count': 0, 'total_analyzed': len(df)}
        
        return {
            'total_analyzed': len(df),
            'bipartisan_count': len(bipartisan_df),
            'bipartisan_percentage': (len(bipartisan_df) / len(df)) * 100,
            'bipartisan_law_rate': (bipartisan_df['is_law'].sum() / len(bipartisan_df)) * 100,
            'overall_law_rate': (df['is_law'].sum() / len(df)) * 100,
            'avg_dem_cosponsors': float(bipartisan_df['dem_cosponsors'].mean()),
            'avg_rep_cosponsors': float(bipartisan_df['rep_cosponsors'].mean())
        }

    def committee_effectiveness(self, congress: int) -> pd.DataFrame:
        """
        Analyze committee effectiveness metrics.
        
        Args:
            congress: Congress number
            
        Returns:
            DataFrame with committee statistics
        """
        sql = """
        SELECT 
            c.system_code,
            c.name,
            c.chamber,
            COUNT(DISTINCT b.id) as bills_referred,
            COUNT(DISTINCT b.id) FILTER (WHERE b.is_law = true) as laws_enacted,
            AVG(b.cosponsors_count) as avg_cosponsors
        FROM committees c
        LEFT JOIN bills b ON b.raw_data::text LIKE '%' || c.system_code || '%'
            AND b.congress = :congress
        GROUP BY c.system_code, c.name, c.chamber
        HAVING COUNT(DISTINCT b.id) > 0
        ORDER BY bills_referred DESC
        """
        
        results = self.db.execute_sql(sql, {'congress': congress})
        df = pd.DataFrame(results)
        
        if not df.empty and 'bills_referred' in df.columns and 'laws_enacted' in df.columns:
            df['success_rate'] = (df['laws_enacted'] / df['bills_referred'] * 100).round(2)
        
        return df

    def compare_congresses(
        self,
        congress_list: List[int]
    ) -> pd.DataFrame:
        """
        Compare metrics across multiple congresses.
        
        Args:
            congress_list: List of congress numbers
            
        Returns:
            DataFrame with comparative statistics
        """
        stats_list = []
        
        for congress in congress_list:
            stats = self.calculate_bill_statistics(congress)
            stats['congress'] = congress
            stats_list.append(stats)
        
        df = pd.DataFrame(stats_list)
        return df

    # ==================== Network Analysis Methods ====================

    def cosponsor_network_metrics(
        self,
        congress: int,
        min_cosponsors: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate network metrics for cosponsor relationships.
        
        Args:
            congress: Congress number
            min_cosponsors: Minimum cosponsors to include bill
            
        Returns:
            Dictionary with network metrics
        """
        sql = """
        SELECT 
            b.id,
            b.sponsors,
            b.raw_data->'cosponsors' as cosponsors,
            b.cosponsors_count
        FROM bills b
        WHERE b.congress = :congress
        AND b.cosponsors_count >= :min_cosponsors
        """
        
        results = self.db.execute_sql(sql, {
            'congress': congress,
            'min_cosponsors': min_cosponsors
        })
        
        if not results:
            return {'error': 'No data available'}
        
        # Build edge list
        edges = []
        member_bills = defaultdict(int)
        
        for row in results:
            sponsors = json.loads(row['sponsors']) if isinstance(row['sponsors'], str) else row['sponsors']
            cosponsors = json.loads(row['cosponsors']) if isinstance(row['cosponsors'], str) else (row['cosponsors'] or [])
            
            if not sponsors:
                continue
            
            sponsor_id = sponsors[0].get('bioguideId')
            if not sponsor_id:
                continue
            
            member_bills[sponsor_id] += 1
            
            for cosponsor in cosponsors:
                cosponsor_id = cosponsor.get('bioguideId')
                if cosponsor_id:
                    edges.append((sponsor_id, cosponsor_id))
                    member_bills[cosponsor_id] += 1
        
        # Calculate metrics
        total_edges = len(edges)
        unique_pairs = len(set(edges))
        total_members = len(member_bills)
        
        return {
            'total_members': total_members,
            'total_edges': total_edges,
            'unique_relationships': unique_pairs,
            'avg_bills_per_member': sum(member_bills.values()) / total_members if total_members > 0 else 0,
            'density': unique_pairs / (total_members * (total_members - 1) / 2) if total_members > 1 else 0,
            'most_active_members': sorted(
                [(k, v) for k, v in member_bills.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    # ==================== Predictive Analysis Methods ====================

    def predict_bill_success(
        self,
        congress: int,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze features correlated with bill success.
        
        Args:
            congress: Congress number
            features: List of features to analyze
            
        Returns:
            Dictionary with correlation analysis
        """
        df = self.get_bills_dataframe(congress=congress)
        
        if df.empty:
            return {'error': 'No data available'}
        
        # Prepare features
        df['is_law_num'] = df['is_law'].astype(int)
        
        correlations = {}
        
        # Cosponsor count correlation
        if 'cosponsors_count' in df.columns:
            corr = df['cosponsors_count'].corr(df['is_law_num'])
            correlations['cosponsors_count'] = float(corr)
        
        # Chamber analysis
        chamber_success = df.groupby('origin_chamber')['is_law_num'].mean().to_dict()
        correlations['chamber_success_rates'] = chamber_success
        
        # Bill type analysis
        type_success = df.groupby('bill_type')['is_law_num'].mean().to_dict()
        correlations['type_success_rates'] = type_success
        
        return correlations
