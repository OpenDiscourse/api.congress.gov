# Congress.gov API Bulk Data Ingestion and Analysis System

A comprehensive Python system for bulk data ingestion, storage, and analysis of Congress.gov API data.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Bulk Data Ingestion](#bulk-data-ingestion)
  - [Data Analysis](#data-analysis)
  - [Querying Data](#querying-data)
- [Module Documentation](#module-documentation)
- [API Reference](#api-reference)
- [Examples](#examples)

## Overview

This system provides a complete solution for:

1. **Bulk Data Ingestion**: Efficiently download and store large volumes of Congressional data
2. **Database Management**: PostgreSQL-based storage with optimized schema and indexes
3. **Data Analysis**: Statistical, temporal, and network analysis capabilities
4. **Pydantic AI Integration**: Type-safe models and intelligent data processing
5. **Research Methods**: Various analytical approaches for Congressional research

## Features

### Data Ingestion
- ✅ Bulk import of bills, members, amendments, committees, and more
- ✅ Incremental updates for recent changes
- ✅ Rate limiting and error handling
- ✅ Progress tracking and logging
- ✅ Automatic data validation with Pydantic

### Database
- ✅ Comprehensive PostgreSQL schema
- ✅ SQL migration scripts for easy setup
- ✅ Optimized indexes for fast queries
- ✅ Full-text search capabilities
- ✅ Materialized views for analytics
- ✅ Automatic timestamp tracking

### Analysis
- ✅ Statistical analysis (means, medians, distributions)
- ✅ Temporal trend analysis
- ✅ Policy area analysis
- ✅ Bipartisan support metrics
- ✅ Committee effectiveness tracking
- ✅ Network analysis (cosponsor relationships)
- ✅ Predictive features correlation

### Query Capabilities
- ✅ Filter by congress, type, date range
- ✅ Random sampling
- ✅ Full-text search
- ✅ Complex criteria queries
- ✅ Cross-congress comparisons

## Installation

### Requirements

- Python 3.8+
- PostgreSQL 12+
- Congress.gov API key ([sign up here](https://api.congress.gov/sign-up/))

### Install Dependencies

```bash
cd python
pip install -r requirements.txt
```

## Database Setup

### Option 1: Automated Setup (Linux/Mac)

```bash
cd python/migrations
chmod +x setup_database.sh
./setup_database.sh
```

### Option 2: Manual Setup

1. Create PostgreSQL database:

```bash
createdb congress_api
```

2. Run migration scripts:

```bash
psql -d congress_api -f migrations/001_initial_schema.sql
psql -d congress_api -f migrations/002_views_and_functions.sql
```

### Database Configuration

Set the database URL as an environment variable:

```bash
export DATABASE_URL="postgresql://congress_user:congress_pass@localhost:5432/congress_api"
```

Or configure in your application code.

## Configuration

### API Key Setup

Create a `secrets.ini` file:

```ini
[cdg_api]
api_auth_key = YOUR_API_KEY_HERE
```

Or set as environment variable:

```bash
export CONGRESS_API_KEY="your_api_key_here"
```

## Usage

### Bulk Data Ingestion

#### Using the CLI

```bash
# Ingest all bills from Congress 118
python congress_cli.py ingest bills --congress 118

# Ingest specific bill type
python congress_cli.py ingest bills --congress 118 --bill-type hr

# Ingest with date range
python congress_cli.py ingest bills --congress 118 \
  --from-date 2023-01-01T00:00:00Z \
  --to-date 2023-12-31T23:59:59Z

# Ingest members
python congress_cli.py ingest members --congress 118

# Ingest amendments
python congress_cli.py ingest amendments --congress 118

# Ingest committees
python congress_cli.py ingest committees

# Sync recent bills (last 7 days)
python congress_cli.py ingest sync-recent --days 7
```

#### Using Python API

```python
from database import DatabaseManager
from bulk_ingest import BulkIngestor

# Initialize
db_manager = DatabaseManager()
ingestor = BulkIngestor(api_key="your_key", db_manager=db_manager)

# Ingest bills
stats = ingestor.ingest_bills(congress=118, bill_type='hr')
print(f"Processed: {stats['processed']}, Created: {stats['created']}")

# Ingest members
stats = ingestor.ingest_members(congress=118)

# Sync recent changes
stats = ingestor.sync_recent_bills(days=7)
```

### Data Analysis

#### Using the CLI

```bash
# Calculate statistics
python congress_cli.py analyze statistics --congress 118

# Temporal analysis
python congress_cli.py analyze temporal --congress 118 --grouping month

# Policy area analysis
python congress_cli.py analyze policy-areas --congress 118

# Bipartisan analysis
python congress_cli.py analyze bipartisan --congress 118

# Committee effectiveness
python congress_cli.py analyze committees-analysis --congress 118
```

#### Using Python API

```python
from database import DatabaseManager
from analysis import CongressDataAnalyzer

# Initialize
db_manager = DatabaseManager()
analyzer = CongressDataAnalyzer(db_manager)

# Get comprehensive statistics
stats = analyzer.calculate_bill_statistics(congress=118)
print(f"Total bills: {stats['total_bills']}")
print(f"Passage rate: {stats['law_passage_rate']:.2%}")

# Temporal analysis
df = analyzer.temporal_analysis(congress=118, grouping='month')
print(df)

# Policy area analysis
policy_stats = analyzer.policy_area_analysis(congress=118)
print(policy_stats)

# Bipartisan analysis
bipartisan = analyzer.bipartisan_analysis(congress=118)
print(f"Bipartisan percentage: {bipartisan['bipartisan_percentage']:.2f}%")

# Committee effectiveness
committees = analyzer.committee_effectiveness(congress=118)
print(committees)

# Network analysis
network = analyzer.cosponsor_network_metrics(congress=118, min_cosponsors=5)
print(f"Total members: {network['total_members']}")
print(f"Network density: {network['density']:.4f}")
```

### Querying Data

#### Using the CLI

```bash
# Query bills
python congress_cli.py query bills --congress 118 --limit 20

# Query only laws
python congress_cli.py query bills --congress 118 --is-law --limit 10

# Get random sample
python congress_cli.py query sample --table bills --size 50
```

#### Using Python API

```python
from database import DatabaseManager
from analysis import CongressDataAnalyzer

db_manager = DatabaseManager()
analyzer = CongressDataAnalyzer(db_manager)

# Get bills as DataFrame
df = analyzer.get_bills_dataframe(congress=118, bill_type='hr', limit=1000)

# Query with multiple criteria
df = analyzer.query_bills_by_criteria(
    start_date='2023-01-01',
    end_date='2023-12-31',
    congress_list=[117, 118],
    min_cosponsors=10,
    chambers=['House']
)

# Get random sample
sample_df = analyzer.get_random_sample('bills', sample_size=100)

# Search bills by keyword
results = db_manager.search_bills('climate change', limit=50)

# Get member statistics
member_stats = db_manager.get_member_statistics('B000944')  # bioguide_id
```

## Module Documentation

### `models.py`

Pydantic models for data validation:

- `Bill`: Legislative bill data
- `Member`: Congress member information
- `Amendment`: Bill amendments
- `Committee`: Congressional committees
- `Nomination`: Presidential nominations
- `Treaty`: International treaties
- `CommitteeReport`: Committee reports
- `Hearing`: Congressional hearings
- `CongressionalRecord`: Congressional Record entries

### `database.py`

Database interaction layer:

- `DatabaseManager`: Main database interface
  - `insert_bill()`: Insert/update bill
  - `insert_member()`: Insert/update member
  - `insert_amendment()`: Insert/update amendment
  - `get_bills()`: Query bills with filters
  - `search_bills()`: Full-text search
  - `log_sync()`: Track API sync operations

### `bulk_ingest.py`

Bulk data ingestion:

- `BulkIngestor`: Main ingestion class
  - `ingest_bills()`: Bulk import bills
  - `ingest_members()`: Bulk import members
  - `ingest_amendments()`: Bulk import amendments
  - `ingest_committees()`: Bulk import committees
  - `sync_recent_bills()`: Incremental updates

### `analysis.py`

Data analysis tools:

- `CongressDataAnalyzer`: Comprehensive analysis
  - `calculate_bill_statistics()`: Statistical metrics
  - `temporal_analysis()`: Time-based trends
  - `policy_area_analysis()`: Policy area breakdown
  - `bipartisan_analysis()`: Bipartisan support metrics
  - `committee_effectiveness()`: Committee performance
  - `cosponsor_network_metrics()`: Network analysis
  - `predict_bill_success()`: Correlation analysis

### `congress_cli.py`

Command-line interface:

- `ingest`: Bulk ingestion commands
- `analyze`: Analysis commands
- `query`: Data query commands

## API Reference

### Bulk Ingestion

```python
ingestor = BulkIngestor(api_key, db_manager, rate_limit_delay=0.75)

# Returns: {'processed': int, 'created': int, 'updated': int, 'failed': int}
stats = ingestor.ingest_bills(
    congress=118,              # Optional: Congress number
    bill_type='hr',            # Optional: Bill type
    from_date='2023-01-01',    # Optional: Start date (ISO format)
    to_date='2023-12-31',      # Optional: End date (ISO format)
    max_pages=10               # Optional: Limit pages
)
```

### Data Analysis

```python
analyzer = CongressDataAnalyzer(db_manager)

# Statistical analysis
stats = analyzer.calculate_bill_statistics(congress=118)
# Returns: {
#   'total_bills': int,
#   'laws_enacted': int,
#   'law_passage_rate': float,
#   'by_chamber': dict,
#   'cosponsors_stats': dict
# }

# Temporal analysis
df = analyzer.temporal_analysis(congress=118, grouping='month')
# Returns: DataFrame with columns: period, total_bills, laws_enacted, avg_cosponsors

# Bipartisan analysis
results = analyzer.bipartisan_analysis(congress=118)
# Returns: {
#   'bipartisan_count': int,
#   'bipartisan_percentage': float,
#   'bipartisan_law_rate': float
# }
```

### Database Queries

```python
# Get bills
bills = db_manager.get_bills(congress=118, bill_type='hr', limit=100)

# Search bills
results = db_manager.search_bills('healthcare', limit=50)

# Get session statistics
stats = db_manager.get_session_statistics(congress=118)
```

## Examples

### Example 1: Complete Ingestion and Analysis Pipeline

```python
from database import DatabaseManager
from bulk_ingest import BulkIngestor
from analysis import CongressDataAnalyzer

# Setup
api_key = "your_api_key"
db_manager = DatabaseManager()
ingestor = BulkIngestor(api_key, db_manager)
analyzer = CongressDataAnalyzer(db_manager)

# Step 1: Ingest data
print("Ingesting bills...")
ingestor.ingest_bills(congress=118, max_pages=5)

print("Ingesting members...")
ingestor.ingest_members(congress=118)

# Step 2: Analyze
print("Calculating statistics...")
stats = analyzer.calculate_bill_statistics(congress=118)
print(f"Total bills: {stats['total_bills']}")
print(f"Laws enacted: {stats['laws_enacted']}")

print("Analyzing bipartisan support...")
bipartisan = analyzer.bipartisan_analysis(congress=118)
print(f"Bipartisan bills: {bipartisan['bipartisan_percentage']:.1f}%")
```

### Example 2: Research Query

```python
from analysis import CongressDataAnalyzer
from database import DatabaseManager

db_manager = DatabaseManager()
analyzer = CongressDataAnalyzer(db_manager)

# Query: Healthcare bills with high bipartisan support in 2023
df = analyzer.query_bills_by_criteria(
    start_date='2023-01-01',
    end_date='2023-12-31',
    congress_list=[118],
    policy_areas=['Health'],
    min_cosponsors=20
)

print(f"Found {len(df)} healthcare bills with 20+ cosponsors")

# Analyze by chamber
chamber_stats = df.groupby('origin_chamber').agg({
    'id': 'count',
    'is_law': 'sum',
    'cosponsors_count': 'mean'
})
print(chamber_stats)
```

### Example 3: Network Analysis

```python
from analysis import CongressDataAnalyzer
from database import DatabaseManager

db_manager = DatabaseManager()
analyzer = CongressDataAnalyzer(db_manager)

# Analyze cosponsor networks
network = analyzer.cosponsor_network_metrics(
    congress=118,
    min_cosponsors=10
)

print(f"Network has {network['total_members']} members")
print(f"Density: {network['density']:.4f}")
print("\nMost active members:")
for member_id, count in network['most_active_members'][:10]:
    print(f"  {member_id}: {count} bills")
```

## Database Schema

### Main Tables

- `congress`: Congressional sessions
- `bills`: Legislative bills
- `members`: Congress members
- `committees`: Congressional committees
- `amendments`: Bill amendments
- `nominations`: Presidential nominations
- `treaties`: International treaties
- `committee_reports`: Committee reports
- `hearings`: Congressional hearings
- `congressional_record`: Congressional Record
- `api_sync_log`: API synchronization logs

### Views

- `recent_bills`: Bills from last 30 days
- `bills_by_status`: Bill counts by status
- `member_activity_summary`: Member activity metrics
- `committee_activity`: Committee activity metrics
- `session_statistics`: Per-session statistics
- `bill_trends`: Materialized view of bill trends

### Functions

- `search_bills(keyword)`: Full-text search
- `get_bills_by_date_range()`: Date-based queries
- `calculate_bill_progression_stats()`: Stage analysis
- `get_member_statistics()`: Member metrics
- `refresh_bill_trends()`: Update materialized views

## Performance Tips

1. **Use indexes**: The schema includes optimized indexes for common queries
2. **Batch operations**: Ingest data in batches rather than one at a time
3. **Rate limiting**: Respect API rate limits (5000 requests/hour)
4. **Incremental updates**: Use `sync_recent_bills()` for daily updates
5. **Materialized views**: Refresh periodically for faster analytics

## Troubleshooting

### Connection Issues

```python
# Test database connection
from database import DatabaseManager
db = DatabaseManager("postgresql://user:pass@localhost/congress_api")
result = db.execute_sql("SELECT version()")
print(result)
```

### API Rate Limiting

If you hit rate limits, adjust the delay:

```python
ingestor = BulkIngestor(api_key, db_manager, rate_limit_delay=1.0)
```

### Large Dataset Memory

For large datasets, process in chunks:

```python
# Use max_pages to limit data
ingestor.ingest_bills(congress=118, max_pages=10)
```

## Contributing

Contributions are welcome! Please ensure:

1. Code follows existing style
2. Add tests for new features
3. Update documentation
4. Follow semantic versioning

## License

CC0 1.0 Universal - Public Domain

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/OpenDiscourse/api.congress.gov/issues)
- Documentation: [Congress.gov API Docs](https://api.congress.gov/)

## Acknowledgments

- Library of Congress for the Congress.gov API
- OpenDiscourse community
