# Congress.gov API Bulk System - Quick Start Guide

Get started with the Congress.gov API Bulk Data Ingestion and Analysis System in minutes!

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (optional, for persistent storage)
- Congress.gov API key ([sign up here](https://api.congress.gov/sign-up/))

## Installation

### 1. Install Dependencies

```bash
cd python
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `secrets.ini` file in the project root:

```ini
[cdg_api]
api_auth_key = YOUR_API_KEY_HERE
```

Or set as environment variable:

```bash
export CONGRESS_API_KEY="your_api_key_here"
```

### 3. Setup Database (Optional)

If you want to persist data, set up PostgreSQL:

```bash
# Linux/Mac
cd python/migrations
./setup_database.sh

# Or manually
createdb congress_api
psql -d congress_api -f migrations/001_initial_schema.sql
psql -d congress_api -f migrations/002_views_and_functions.sql
```

Set database connection:

```bash
export DATABASE_URL="postgresql://congress_user:congress_pass@localhost:5432/congress_api"
```

## Quick Examples

### Example 1: Validate Data with Pydantic Models

```python
from models import Bill, Member

# Create a validated bill instance
bill = Bill(
    congress=118,
    type='hr',
    number=1234,
    title='Example Bill'
)
print(f"Bill: {bill.congress}-{bill.bill_type}{bill.bill_number}")
```

### Example 2: Bulk Ingest Bills

```bash
# Using CLI
python congress_cli.py ingest bills --congress 118 --bill-type hr --max-pages 2

# Or in Python
from database import DatabaseManager
from bulk_ingest import BulkIngestor

db_manager = DatabaseManager()
ingestor = BulkIngestor(api_key="your_key", db_manager=db_manager)

stats = ingestor.ingest_bills(congress=118, bill_type='hr', max_pages=2)
print(f"Processed {stats['processed']} bills")
```

### Example 3: Analyze Congressional Data

```bash
# Using CLI
python congress_cli.py analyze statistics --congress 118
python congress_cli.py analyze bipartisan --congress 118

# Or in Python
from analysis import CongressDataAnalyzer
from database import DatabaseManager

analyzer = CongressDataAnalyzer(DatabaseManager())

# Get statistics
stats = analyzer.calculate_bill_statistics(congress=118)
print(f"Total bills: {stats['total_bills']}")
print(f"Passage rate: {stats['law_passage_rate']:.2%}")

# Analyze bipartisan support
bipartisan = analyzer.bipartisan_analysis(congress=118)
print(f"Bipartisan bills: {bipartisan['bipartisan_percentage']:.1f}%")
```

### Example 4: Query and Filter Data

```python
from analysis import CongressDataAnalyzer
from database import DatabaseManager

analyzer = CongressDataAnalyzer(DatabaseManager())

# Get bills as DataFrame
df = analyzer.get_bills_dataframe(
    congress=118,
    bill_type='hr',
    is_law=True,
    limit=50
)

# Query with complex criteria
df = analyzer.query_bills_by_criteria(
    start_date='2023-01-01',
    end_date='2023-12-31',
    congress_list=[118],
    min_cosponsors=10,
    chambers=['House']
)

print(f"Found {len(df)} bills matching criteria")
```

## Common Use Cases

### Research Workflow: Healthcare Legislation

```python
from database import DatabaseManager
from bulk_ingest import BulkIngestor
from analysis import CongressDataAnalyzer

# Setup
api_key = "your_api_key"
db_manager = DatabaseManager()
ingestor = BulkIngestor(api_key, db_manager)
analyzer = CongressDataAnalyzer(db_manager)

# 1. Ingest data
print("Ingesting bills...")
ingestor.ingest_bills(congress=118, max_pages=10)

# 2. Query healthcare bills
df = analyzer.query_bills_by_criteria(
    start_date='2023-01-01',
    end_date='2023-12-31',
    congress_list=[118],
    policy_areas=['Health'],
    min_cosponsors=5
)

print(f"Found {len(df)} healthcare bills")

# 3. Analyze bipartisan support
bipartisan = analyzer.bipartisan_analysis(congress=118)
print(f"Bipartisan support: {bipartisan['bipartisan_percentage']:.1f}%")

# 4. Export results
df.to_csv('healthcare_bills_2023.csv', index=False)
```

### Daily Sync Script

```python
from database import DatabaseManager
from bulk_ingest import BulkIngestor

# Sync recent changes daily
api_key = "your_api_key"
db_manager = DatabaseManager()
ingestor = BulkIngestor(api_key, db_manager)

# Sync bills from last 7 days
stats = ingestor.sync_recent_bills(days=7)
print(f"Synced {stats['processed']} bills")
print(f"Created: {stats['created']}, Updated: {stats['updated']}")
```

## CLI Commands Cheat Sheet

```bash
# Ingestion
python congress_cli.py ingest bills --congress 118
python congress_cli.py ingest members --congress 118
python congress_cli.py ingest amendments --congress 118
python congress_cli.py ingest committees
python congress_cli.py ingest sync-recent --days 7

# Analysis
python congress_cli.py analyze statistics --congress 118
python congress_cli.py analyze temporal --congress 118 --grouping month
python congress_cli.py analyze policy-areas --congress 118
python congress_cli.py analyze bipartisan --congress 118
python congress_cli.py analyze committees-analysis --congress 118

# Queries
python congress_cli.py query bills --congress 118 --limit 20
python congress_cli.py query bills --congress 118 --is-law --limit 10
python congress_cli.py query sample --table bills --size 50
```

## What's Included

### Database Schema
- 10+ normalized tables (bills, members, committees, amendments, etc.)
- Optimized indexes for fast queries
- Full-text search capabilities
- Analytical views and functions

### Data Models
- Type-safe Pydantic models
- Validation and serialization
- Support for all major API endpoints

### Analysis Functions
- Statistical analysis
- Temporal trends
- Policy area breakdowns
- Bipartisan support metrics
- Committee effectiveness
- Network analysis
- Predictive correlations

### CLI Tool
- Simple commands for all operations
- Beautiful rich-formatted output
- Progress bars and status updates

## Next Steps

1. **Read the full documentation**: [README_BULK_SYSTEM.md](README_BULK_SYSTEM.md)
2. **Run the examples**: `python example_usage.py`
3. **Explore the CLI**: `python congress_cli.py --help`
4. **Check the test suite**: Files in `tests/` directory
5. **Review the SQL migrations**: Files in `migrations/` directory

## Support

- **Documentation**: [README_BULK_SYSTEM.md](README_BULK_SYSTEM.md)
- **Issues**: [GitHub Issues](https://github.com/OpenDiscourse/api.congress.gov/issues)
- **API Docs**: [Congress.gov API](https://api.congress.gov/)

## Tips

1. **Start small**: Use `--max-pages 2` when testing to limit API calls
2. **Rate limiting**: The system respects API limits (5000 requests/hour)
3. **Incremental updates**: Use `sync-recent` for daily updates instead of full re-imports
4. **Database indexes**: The schema includes optimized indexes for common queries
5. **Pandas integration**: All analysis functions return DataFrames for easy manipulation

## Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### "Database connection failed"
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
export DATABASE_URL="postgresql://user:password@localhost:5432/congress_api"
```

### "API rate limit exceeded"
The system has built-in rate limiting. If you're still hitting limits, increase the delay:
```python
ingestor = BulkIngestor(api_key, db_manager, rate_limit_delay=1.0)
```

Happy analyzing! 🎉
