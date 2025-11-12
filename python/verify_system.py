#!/usr/bin/env python3
"""
System Verification Script

This script verifies that all components of the Congress.gov API Bulk System
are properly installed and functional.

@copyright: 2024, OpenDiscourse
@license: CC0 1.0
"""
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def check_imports():
    """Check that all required modules can be imported."""
    console.print("\n[bold blue]Checking Module Imports...[/bold blue]")
    
    modules = [
        ('models', 'Pydantic data models'),
        ('database', 'Database interaction layer'),
        ('bulk_ingest', 'Bulk data ingestion'),
        ('analysis', 'Data analysis functions'),
        ('congress_cli', 'Command-line interface'),
        ('cdg_client', 'API client'),
    ]
    
    table = Table(title="Module Import Check")
    table.add_column("Module", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    
    all_success = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            table.add_row(module_name, description, "✓ OK")
        except ImportError as e:
            table.add_row(module_name, description, f"✗ FAILED: {e}")
            all_success = False
    
    console.print(table)
    return all_success


def check_models():
    """Check that Pydantic models work correctly."""
    console.print("\n[bold blue]Checking Pydantic Models...[/bold blue]")
    
    try:
        from models import Bill, Member, Amendment, Committee, Sponsor
        
        # Test Bill model
        bill = Bill(
            congress=118,
            type='hr',
            number=1234,
            title='Test Bill'
        )
        
        # Test Member model
        member = Member(
            bioguideId='B000944',
            firstName='Sherrod',
            lastName='Brown'
        )
        
        # Test Amendment model
        amendment = Amendment(
            congress=118,
            type='hamdt',
            number=123
        )
        
        # Test Committee model
        committee = Committee(
            systemCode='hsgo00',
            name='Test Committee'
        )
        
        # Test Sponsor model
        sponsor = Sponsor(
            bioguideId='B000944',
            fullName='Sen. Brown'
        )
        
        console.print("[green]✓ All Pydantic models working correctly[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Model validation failed: {e}[/red]")
        return False


def check_database_manager():
    """Check that DatabaseManager can be instantiated."""
    console.print("\n[bold blue]Checking Database Manager...[/bold blue]")
    
    try:
        from database import DatabaseManager
        
        # Test instantiation (won't connect to actual DB without URL)
        db = DatabaseManager("postgresql://test:test@localhost/test")
        
        console.print("[green]✓ DatabaseManager instantiated successfully[/green]")
        console.print("[yellow]  Note: Actual database connection requires valid DATABASE_URL[/yellow]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ DatabaseManager check failed: {e}[/red]")
        return False


def check_bulk_ingestor():
    """Check that BulkIngestor can be instantiated."""
    console.print("\n[bold blue]Checking Bulk Ingestor...[/bold blue]")
    
    try:
        from bulk_ingest import BulkIngestor
        from database import DatabaseManager
        
        db = DatabaseManager("postgresql://test:test@localhost/test")
        ingestor = BulkIngestor("test_api_key", db)
        
        console.print("[green]✓ BulkIngestor instantiated successfully[/green]")
        console.print("[yellow]  Note: Actual ingestion requires valid API key and database[/yellow]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ BulkIngestor check failed: {e}[/red]")
        return False


def check_analyzer():
    """Check that CongressDataAnalyzer can be instantiated."""
    console.print("\n[bold blue]Checking Data Analyzer...[/bold blue]")
    
    try:
        from analysis import CongressDataAnalyzer
        from database import DatabaseManager
        
        db = DatabaseManager("postgresql://test:test@localhost/test")
        analyzer = CongressDataAnalyzer(db)
        
        console.print("[green]✓ CongressDataAnalyzer instantiated successfully[/green]")
        console.print("[yellow]  Note: Actual analysis requires data in database[/yellow]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ CongressDataAnalyzer check failed: {e}[/red]")
        return False


def check_cli():
    """Check that CLI can be imported."""
    console.print("\n[bold blue]Checking CLI Interface...[/bold blue]")
    
    try:
        import congress_cli
        
        console.print("[green]✓ CLI module imported successfully[/green]")
        console.print("[yellow]  Run 'python congress_cli.py --help' for usage[/yellow]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ CLI check failed: {e}[/red]")
        return False


def check_dependencies():
    """Check that key dependencies are available."""
    console.print("\n[bold blue]Checking Dependencies...[/bold blue]")
    
    dependencies = [
        ('requests', 'HTTP library for API calls'),
        ('pydantic', 'Data validation'),
        ('sqlalchemy', 'Database ORM'),
        ('pandas', 'Data analysis'),
        ('click', 'CLI framework'),
        ('rich', 'Terminal formatting'),
        ('tqdm', 'Progress bars'),
    ]
    
    table = Table(title="Dependency Check")
    table.add_column("Package", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    
    all_success = True
    for package, description in dependencies:
        try:
            __import__(package)
            table.add_row(package, description, "✓ Installed")
        except ImportError:
            table.add_row(package, description, "✗ Missing")
            all_success = False
    
    console.print(table)
    
    if not all_success:
        console.print("\n[yellow]Missing dependencies can be installed with:[/yellow]")
        console.print("  pip install -r requirements.txt")
    
    return all_success


def check_files():
    """Check that all expected files exist."""
    console.print("\n[bold blue]Checking File Structure...[/bold blue]")
    
    import os
    
    files = [
        ('models.py', 'Pydantic models'),
        ('database.py', 'Database layer'),
        ('bulk_ingest.py', 'Bulk ingestion'),
        ('analysis.py', 'Analysis functions'),
        ('congress_cli.py', 'CLI tool'),
        ('requirements.txt', 'Dependencies'),
        ('README_BULK_SYSTEM.md', 'Main documentation'),
        ('QUICKSTART.md', 'Quick start guide'),
        ('migrations/001_initial_schema.sql', 'Database schema'),
        ('migrations/002_views_and_functions.sql', 'Database views'),
        ('migrations/setup_database.sh', 'Setup script'),
    ]
    
    table = Table(title="File Structure Check")
    table.add_column("File", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    
    all_exist = True
    for filepath, description in files:
        if os.path.exists(filepath):
            table.add_row(filepath, description, "✓ Exists")
        else:
            table.add_row(filepath, description, "✗ Missing")
            all_exist = False
    
    console.print(table)
    return all_exist


def main():
    """Run all verification checks."""
    console.print(Panel.fit(
        "[bold cyan]Congress.gov API Bulk System[/bold cyan]\n"
        "[white]System Verification[/white]",
        border_style="blue"
    ))
    
    checks = [
        ("File Structure", check_files),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_imports),
        ("Pydantic Models", check_models),
        ("Database Manager", check_database_manager),
        ("Bulk Ingestor", check_bulk_ingestor),
        ("Data Analyzer", check_analyzer),
        ("CLI Interface", check_cli),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            console.print(f"[red]✗ {check_name} check failed with error: {e}[/red]")
            results.append((check_name, False))
    
    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold]Verification Summary[/bold]")
    console.print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        console.print(f"{check_name:.<40} {status}")
    
    console.print("=" * 60)
    console.print(f"[bold]Results: {passed}/{total} checks passed[/bold]")
    
    if passed == total:
        console.print("\n[green]✓ All verification checks passed![/green]")
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Configure your API key in secrets.ini")
        console.print("2. Set up PostgreSQL database (see QUICKSTART.md)")
        console.print("3. Run: python congress_cli.py --help")
        console.print("4. Read README_BULK_SYSTEM.md for full documentation")
        return 0
    else:
        console.print(f"\n[yellow]⚠ {total - passed} check(s) failed[/yellow]")
        console.print("\n[bold]Troubleshooting:[/bold]")
        console.print("1. Run: pip install -r requirements.txt")
        console.print("2. Ensure all files are present")
        console.print("3. Check Python version (3.8+ required)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
