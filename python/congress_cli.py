#!/usr/bin/env python3
"""
Congress.gov API CLI - Command-line interface for bulk ingestion and analysis.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
import os
import sys
from configparser import ConfigParser
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from database import DatabaseManager
from bulk_ingest import BulkIngestor
from analysis import CongressDataAnalyzer


console = Console()


def load_api_key():
    """Load API key from secrets.ini file."""
    config_paths = [
        Path('../secrets.ini'),
        Path('secrets.ini'),
        Path.home() / '.congress_api' / 'secrets.ini'
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            config = ConfigParser()
            config.read(config_path)
            return config.get('cdg_api', 'api_auth_key', fallback=None)
    
    # Try environment variable
    return os.getenv('CONGRESS_API_KEY')


@click.group()
@click.option('--db-url', envvar='DATABASE_URL', help='Database connection URL')
@click.pass_context
def cli(ctx, db_url):
    """Congress.gov API CLI - Bulk ingestion and analysis tools."""
    ctx.ensure_object(dict)
    ctx.obj['db_manager'] = DatabaseManager(db_url)


@cli.group()
def ingest():
    """Bulk data ingestion commands."""
    pass


@ingest.command()
@click.option('--congress', type=int, help='Congress number (e.g., 118)')
@click.option('--bill-type', help='Bill type (hr, s, hjres, sjres)')
@click.option('--from-date', help='Start date (ISO format)')
@click.option('--to-date', help='End date (ISO format)')
@click.option('--max-pages', type=int, help='Maximum pages to fetch')
@click.pass_context
def bills(ctx, congress, bill_type, from_date, to_date, max_pages):
    """Ingest bills from Congress.gov API."""
    api_key = load_api_key()
    if not api_key:
        console.print("[red]Error: API key not found. Set CONGRESS_API_KEY or configure secrets.ini[/red]")
        sys.exit(1)
    
    db_manager = ctx.obj['db_manager']
    ingestor = BulkIngestor(api_key, db_manager)
    
    console.print(f"[blue]Starting bill ingestion...[/blue]")
    if congress:
        console.print(f"  Congress: {congress}")
    if bill_type:
        console.print(f"  Type: {bill_type}")
    if from_date and to_date:
        console.print(f"  Date range: {from_date} to {to_date}")
    
    stats = ingestor.ingest_bills(
        congress=congress,
        bill_type=bill_type,
        from_date=from_date,
        to_date=to_date,
        max_pages=max_pages
    )
    
    # Display results
    table = Table(title="Ingestion Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    table.add_row("Processed", str(stats['processed']))
    table.add_row("Created", str(stats['created']))
    table.add_row("Updated", str(stats['updated']))
    table.add_row("Failed", str(stats['failed']))
    
    console.print(table)


@ingest.command()
@click.option('--congress', type=int, help='Congress number')
@click.option('--max-pages', type=int, help='Maximum pages to fetch')
@click.pass_context
def members(ctx, congress, max_pages):
    """Ingest members from Congress.gov API."""
    api_key = load_api_key()
    if not api_key:
        console.print("[red]Error: API key not found[/red]")
        sys.exit(1)
    
    db_manager = ctx.obj['db_manager']
    ingestor = BulkIngestor(api_key, db_manager)
    
    console.print("[blue]Starting member ingestion...[/blue]")
    stats = ingestor.ingest_members(congress=congress, max_pages=max_pages)
    
    table = Table(title="Ingestion Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    for key, value in stats.items():
        if key != 'errors':
            table.add_row(key.title(), str(value))
    
    console.print(table)


@ingest.command()
@click.option('--congress', type=int, help='Congress number')
@click.option('--max-pages', type=int, help='Maximum pages to fetch')
@click.pass_context
def amendments(ctx, congress, max_pages):
    """Ingest amendments from Congress.gov API."""
    api_key = load_api_key()
    if not api_key:
        console.print("[red]Error: API key not found[/red]")
        sys.exit(1)
    
    db_manager = ctx.obj['db_manager']
    ingestor = BulkIngestor(api_key, db_manager)
    
    console.print("[blue]Starting amendment ingestion...[/blue]")
    stats = ingestor.ingest_amendments(congress=congress, max_pages=max_pages)
    
    table = Table(title="Ingestion Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    for key, value in stats.items():
        if key != 'errors':
            table.add_row(key.title(), str(value))
    
    console.print(table)


@ingest.command()
@click.option('--max-pages', type=int, help='Maximum pages to fetch')
@click.pass_context
def committees(ctx, max_pages):
    """Ingest committees from Congress.gov API."""
    api_key = load_api_key()
    if not api_key:
        console.print("[red]Error: API key not found[/red]")
        sys.exit(1)
    
    db_manager = ctx.obj['db_manager']
    ingestor = BulkIngestor(api_key, db_manager)
    
    console.print("[blue]Starting committee ingestion...[/blue]")
    stats = ingestor.ingest_committees(max_pages=max_pages)
    
    table = Table(title="Ingestion Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    for key, value in stats.items():
        if key != 'errors':
            table.add_row(key.title(), str(value))
    
    console.print(table)


@ingest.command()
@click.option('--days', type=int, default=7, help='Days to look back')
@click.pass_context
def sync_recent(ctx, days):
    """Sync recent bills (incremental update)."""
    api_key = load_api_key()
    if not api_key:
        console.print("[red]Error: API key not found[/red]")
        sys.exit(1)
    
    db_manager = ctx.obj['db_manager']
    ingestor = BulkIngestor(api_key, db_manager)
    
    console.print(f"[blue]Syncing bills from last {days} days...[/blue]")
    stats = ingestor.sync_recent_bills(days=days)
    
    table = Table(title="Sync Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    for key, value in stats.items():
        if key != 'errors':
            table.add_row(key.title(), str(value))
    
    console.print(table)


@cli.group()
def analyze():
    """Data analysis commands."""
    pass


@analyze.command()
@click.option('--congress', type=int, required=True, help='Congress number')
@click.pass_context
def statistics(ctx, congress):
    """Calculate comprehensive bill statistics."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    console.print(f"[blue]Calculating statistics for Congress {congress}...[/blue]")
    stats = analyzer.calculate_bill_statistics(congress)
    
    if 'error' in stats:
        console.print(f"[red]Error: {stats['error']}[/red]")
        return
    
    # Display results
    console.print(f"\n[bold]Congress {congress} Statistics[/bold]")
    console.print(f"Total Bills: {stats['total_bills']}")
    console.print(f"Laws Enacted: {stats['laws_enacted']}")
    console.print(f"Passage Rate: {stats['law_passage_rate']:.2%}")
    
    # By chamber
    console.print("\n[bold]By Chamber:[/bold]")
    for chamber, count in stats['by_chamber'].items():
        console.print(f"  {chamber}: {count}")
    
    # Cosponsor stats
    console.print("\n[bold]Cosponsor Statistics:[/bold]")
    cs_stats = stats['cosponsors_stats']
    console.print(f"  Mean: {cs_stats['mean']:.2f}")
    console.print(f"  Median: {cs_stats['median']:.2f}")
    console.print(f"  Std Dev: {cs_stats['std']:.2f}")
    console.print(f"  Max: {cs_stats['max']}")


@analyze.command()
@click.option('--congress', type=int, required=True, help='Congress number')
@click.option('--grouping', type=click.Choice(['day', 'week', 'month', 'quarter']), default='month')
@click.pass_context
def temporal(ctx, congress, grouping):
    """Analyze temporal trends in bill introduction."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    console.print(f"[blue]Analyzing temporal trends for Congress {congress}...[/blue]")
    df = analyzer.temporal_analysis(congress, grouping)
    
    if df.empty:
        console.print("[red]No data available[/red]")
        return
    
    table = Table(title=f"Temporal Analysis - {grouping.title()}ly")
    table.add_column("Period", style="cyan")
    table.add_column("Bills", style="green")
    table.add_column("Laws", style="yellow")
    table.add_column("Avg Cosponsors", style="magenta")
    
    for _, row in df.iterrows():
        table.add_row(
            str(row['period']),
            str(row['total_bills']),
            str(int(row['laws_enacted'])),
            f"{row['avg_cosponsors']:.1f}"
        )
    
    console.print(table)


@analyze.command()
@click.option('--congress', type=int, help='Congress number')
@click.pass_context
def policy_areas(ctx, congress):
    """Analyze bills by policy area."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    console.print("[blue]Analyzing policy areas...[/blue]")
    df = analyzer.policy_area_analysis(congress)
    
    if df.empty:
        console.print("[red]No data available[/red]")
        return
    
    table = Table(title="Policy Area Analysis")
    table.add_column("Policy Area", style="cyan")
    table.add_column("Bills", style="green")
    table.add_column("Laws", style="yellow")
    table.add_column("Avg Cosponsors", style="magenta")
    
    for _, row in df.head(20).iterrows():
        table.add_row(
            row['policy_area'],
            str(row['total_bills']),
            str(int(row['laws_enacted'])),
            f"{row['avg_cosponsors']:.1f}"
        )
    
    console.print(table)


@analyze.command()
@click.option('--congress', type=int, required=True, help='Congress number')
@click.pass_context
def bipartisan(ctx, congress):
    """Analyze bipartisan support for bills."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    console.print(f"[blue]Analyzing bipartisan support for Congress {congress}...[/blue]")
    results = analyzer.bipartisan_analysis(congress)
    
    if 'error' in results:
        console.print(f"[red]Error: {results['error']}[/red]")
        return
    
    console.print(f"\n[bold]Bipartisan Analysis[/bold]")
    console.print(f"Total Bills Analyzed: {results['total_analyzed']}")
    console.print(f"Bipartisan Bills: {results['bipartisan_count']}")
    console.print(f"Bipartisan Percentage: {results['bipartisan_percentage']:.2f}%")
    console.print(f"Bipartisan Law Rate: {results['bipartisan_law_rate']:.2f}%")
    console.print(f"Overall Law Rate: {results['overall_law_rate']:.2f}%")
    console.print(f"\nAverage Democrat Cosponsors: {results['avg_dem_cosponsors']:.1f}")
    console.print(f"Average Republican Cosponsors: {results['avg_rep_cosponsors']:.1f}")


@analyze.command()
@click.option('--congress', type=int, required=True, help='Congress number')
@click.pass_context
def committees_analysis(ctx, congress):
    """Analyze committee effectiveness."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    console.print(f"[blue]Analyzing committee effectiveness for Congress {congress}...[/blue]")
    df = analyzer.committee_effectiveness(congress)
    
    if df.empty:
        console.print("[red]No data available[/red]")
        return
    
    table = Table(title="Committee Effectiveness")
    table.add_column("Committee", style="cyan")
    table.add_column("Chamber", style="blue")
    table.add_column("Bills", style="green")
    table.add_column("Laws", style="yellow")
    table.add_column("Success %", style="magenta")
    
    for _, row in df.head(20).iterrows():
        table.add_row(
            row['name'][:50],
            str(row['chamber']),
            str(row['bills_referred']),
            str(row['laws_enacted']),
            f"{row.get('success_rate', 0):.1f}%"
        )
    
    console.print(table)


@cli.group()
def query():
    """Query data with various filters."""
    pass


@query.command()
@click.option('--congress', type=int, help='Congress number')
@click.option('--type', 'bill_type', help='Bill type')
@click.option('--is-law', is_flag=True, help='Filter for laws only')
@click.option('--limit', type=int, default=10, help='Number of results')
@click.pass_context
def bills(ctx, congress, bill_type, is_law, limit):
    """Query bills with filters."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    df = analyzer.get_bills_dataframe(
        congress=congress,
        bill_type=bill_type,
        is_law=is_law if is_law else None,
        limit=limit
    )
    
    if df.empty:
        console.print("[red]No bills found[/red]")
        return
    
    table = Table(title="Bills Query Results")
    table.add_column("Congress", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("Number", style="green")
    table.add_column("Title", style="yellow", max_width=60)
    table.add_column("Law", style="magenta")
    
    for _, row in df.iterrows():
        table.add_row(
            str(row['congress']),
            row['bill_type'],
            str(row['bill_number']),
            row['title'][:60] if row['title'] else '',
            '✓' if row['is_law'] else ''
        )
    
    console.print(table)


@query.command()
@click.option('--table', required=True, help='Table name')
@click.option('--size', type=int, default=10, help='Sample size')
@click.pass_context
def sample(ctx, table, size):
    """Get random sample from table."""
    db_manager = ctx.obj['db_manager']
    analyzer = CongressDataAnalyzer(db_manager)
    
    try:
        df = analyzer.get_random_sample(table, size)
        console.print(f"[green]Retrieved {len(df)} random records from {table}[/green]")
        console.print(df.head(10))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli(obj={})
