#!/usr/bin/env python3
"""
Example usage of the Congress.gov API Bulk System.

This script demonstrates the key features of the system.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
from models import Bill, Member, Sponsor
from database import DatabaseManager
from analysis import CongressDataAnalyzer


def example_models():
    """Demonstrate Pydantic model validation."""
    print("=" * 60)
    print("EXAMPLE 1: Pydantic Model Validation")
    print("=" * 60)
    
    # Create a Bill instance
    bill_data = {
        'congress': 118,
        'type': 'hr',
        'number': 1234,
        'title': 'Example Healthcare Reform Act',
        'originChamber': 'House',
        'cosponsorsCount': 42
    }
    
    bill = Bill(**bill_data)
    print(f"\nBill Created:")
    print(f"  Congress: {bill.congress}")
    print(f"  Type: {bill.bill_type}")
    print(f"  Number: {bill.bill_number}")
    print(f"  Title: {bill.title}")
    print(f"  Cosponsors: {bill.cosponsors_count}")
    
    # Create a Member instance
    member_data = {
        'bioguideId': 'B000944',
        'firstName': 'Sherrod',
        'lastName': 'Brown',
        'party': 'D',
        'state': 'OH'
    }
    
    member = Member(**member_data)
    print(f"\nMember Created:")
    print(f"  Name: {member.first_name} {member.last_name}")
    print(f"  Party: {member.party}")
    print(f"  State: {member.state}")
    print(f"  BioGuide ID: {member.bioguide_id}")


def example_database_connection():
    """Demonstrate database connection."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Database Connection")
    print("=" * 60)
    
    # Note: This requires a running PostgreSQL instance
    # For demo purposes, we'll show the connection string format
    connection_string = "postgresql://congress_user:congress_pass@localhost:5432/congress_api"
    
    print(f"\nDatabase Connection String Format:")
    print(f"  {connection_string}")
    print("\nTo connect:")
    print("  db_manager = DatabaseManager(connection_string)")
    print("  # or use environment variable DATABASE_URL")
    print("\nAvailable database methods:")
    print("  - insert_bill(bill_data)")
    print("  - insert_member(member_data)")
    print("  - insert_amendment(amendment_data)")
    print("  - get_bills(congress, bill_type, limit)")
    print("  - search_bills(keyword)")
    print("  - get_session_statistics(congress)")


def example_bulk_ingestion():
    """Demonstrate bulk ingestion usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Bulk Data Ingestion")
    print("=" * 60)
    
    print("\nBulk ingestion example (pseudo-code):")
    print("""
    from bulk_ingest import BulkIngestor
    from database import DatabaseManager
    
    # Initialize
    api_key = "your_api_key_here"
    db_manager = DatabaseManager()
    ingestor = BulkIngestor(api_key, db_manager)
    
    # Ingest bills from Congress 118
    stats = ingestor.ingest_bills(congress=118, bill_type='hr', max_pages=5)
    print(f"Processed: {stats['processed']}")
    print(f"Created: {stats['created']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    
    # Ingest members
    stats = ingestor.ingest_members(congress=118)
    
    # Sync recent bills (last 7 days)
    stats = ingestor.sync_recent_bills(days=7)
    """)


def example_analysis():
    """Demonstrate analysis capabilities."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Data Analysis")
    print("=" * 60)
    
    print("\nAnalysis examples (pseudo-code):")
    print("""
    from analysis import CongressDataAnalyzer
    from database import DatabaseManager
    
    # Initialize
    db_manager = DatabaseManager()
    analyzer = CongressDataAnalyzer(db_manager)
    
    # Calculate comprehensive statistics
    stats = analyzer.calculate_bill_statistics(congress=118)
    print(f"Total bills: {stats['total_bills']}")
    print(f"Laws enacted: {stats['laws_enacted']}")
    print(f"Passage rate: {stats['law_passage_rate']:.2%}")
    
    # Temporal analysis - track trends over time
    df = analyzer.temporal_analysis(congress=118, grouping='month')
    # Returns DataFrame with: period, total_bills, laws_enacted, avg_cosponsors
    
    # Policy area analysis
    policy_stats = analyzer.policy_area_analysis(congress=118)
    # Returns DataFrame with bills grouped by policy area
    
    # Bipartisan analysis
    bipartisan = analyzer.bipartisan_analysis(congress=118)
    print(f"Bipartisan bills: {bipartisan['bipartisan_percentage']:.1f}%")
    print(f"Bipartisan law rate: {bipartisan['bipartisan_law_rate']:.1f}%")
    
    # Committee effectiveness
    committees = analyzer.committee_effectiveness(congress=118)
    # Returns DataFrame with committee statistics
    
    # Network analysis
    network = analyzer.cosponsor_network_metrics(congress=118, min_cosponsors=5)
    print(f"Network members: {network['total_members']}")
    print(f"Network density: {network['density']:.4f}")
    """)


def example_queries():
    """Demonstrate query capabilities."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Data Queries")
    print("=" * 60)
    
    print("\nQuery examples (pseudo-code):")
    print("""
    from analysis import CongressDataAnalyzer
    from database import DatabaseManager
    
    db_manager = DatabaseManager()
    analyzer = CongressDataAnalyzer(db_manager)
    
    # Get bills as DataFrame
    df = analyzer.get_bills_dataframe(
        congress=118,
        bill_type='hr',
        is_law=True,
        limit=100
    )
    
    # Complex query with multiple criteria
    df = analyzer.query_bills_by_criteria(
        start_date='2023-01-01',
        end_date='2023-12-31',
        congress_list=[117, 118],
        policy_areas=['Health', 'Education'],
        min_cosponsors=10,
        chambers=['House']
    )
    
    # Random sampling
    sample_df = analyzer.get_random_sample('bills', sample_size=100)
    
    # Full-text search
    results = db_manager.search_bills('climate change', limit=50)
    
    # Get member statistics
    member_stats = db_manager.get_member_statistics('B000944')
    print(f"Bills sponsored: {member_stats['bills_sponsored']}")
    """)


def example_cli():
    """Demonstrate CLI usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Command-Line Interface")
    print("=" * 60)
    
    print("\nCLI Usage Examples:")
    print("\n# Ingest bills")
    print("python congress_cli.py ingest bills --congress 118 --bill-type hr")
    
    print("\n# Ingest with date range")
    print("python congress_cli.py ingest bills --congress 118 \\")
    print("  --from-date 2023-01-01T00:00:00Z \\")
    print("  --to-date 2023-12-31T23:59:59Z")
    
    print("\n# Sync recent bills")
    print("python congress_cli.py ingest sync-recent --days 7")
    
    print("\n# Calculate statistics")
    print("python congress_cli.py analyze statistics --congress 118")
    
    print("\n# Temporal analysis")
    print("python congress_cli.py analyze temporal --congress 118 --grouping month")
    
    print("\n# Bipartisan analysis")
    print("python congress_cli.py analyze bipartisan --congress 118")
    
    print("\n# Query bills")
    print("python congress_cli.py query bills --congress 118 --is-law --limit 20")
    
    print("\n# Random sample")
    print("python congress_cli.py query sample --table bills --size 50")


def example_research_workflow():
    """Demonstrate a complete research workflow."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Complete Research Workflow")
    print("=" * 60)
    
    print("\nResearch Question: Healthcare legislation bipartisan support in 2023")
    print("\nWorkflow (pseudo-code):")
    print("""
    # Step 1: Ingest data
    ingestor.ingest_bills(congress=118, max_pages=20)
    ingestor.ingest_members(congress=118)
    
    # Step 2: Query healthcare bills
    df = analyzer.query_bills_by_criteria(
        start_date='2023-01-01',
        end_date='2023-12-31',
        congress_list=[118],
        policy_areas=['Health'],
        min_cosponsors=5
    )
    print(f"Found {len(df)} healthcare bills")
    
    # Step 3: Analyze bipartisan support
    bipartisan = analyzer.bipartisan_analysis(congress=118)
    
    # Step 4: Committee analysis
    committees = analyzer.committee_effectiveness(congress=118)
    health_committees = committees[committees['name'].str.contains('Health', na=False)]
    
    # Step 5: Temporal trends
    trends = analyzer.temporal_analysis(congress=118, grouping='month')
    
    # Step 6: Network analysis
    network = analyzer.cosponsor_network_metrics(congress=118, min_cosponsors=10)
    
    # Step 7: Export results
    df.to_csv('healthcare_bills_2023.csv', index=False)
    bipartisan_summary = {
        'total_bills': len(df),
        'bipartisan_percentage': bipartisan['bipartisan_percentage'],
        'law_rate': bipartisan['bipartisan_law_rate']
    }
    """)


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CONGRESS.GOV API BULK SYSTEM - USAGE EXAMPLES")
    print("=" * 60)
    
    example_models()
    example_database_connection()
    example_bulk_ingestion()
    example_analysis()
    example_queries()
    example_cli()
    example_research_workflow()
    
    print("\n" + "=" * 60)
    print("For more information, see README_BULK_SYSTEM.md")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
