#!/bin/bash
# Congress.gov API Database Setup Script
# This script creates the PostgreSQL database and runs all migrations

set -e

# Default configuration
DB_NAME="${DB_NAME:-congress_api}"
DB_USER="${DB_USER:-congress_user}"
DB_PASSWORD="${DB_PASSWORD:-congress_pass}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "Congress.gov API Database Setup"
echo "================================"
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST:$DB_PORT"
echo ""

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL client (psql) is not installed."
    echo "Please install PostgreSQL and try again."
    exit 1
fi

# Create database and user if they don't exist
echo "Creating database and user..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true

# Run migrations
echo ""
echo "Running migrations..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for migration in "$SCRIPT_DIR"/*.sql; do
    if [ -f "$migration" ]; then
        echo "Applying $(basename "$migration")..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$migration"
    fi
done

echo ""
echo "Database setup completed successfully!"
echo ""
echo "Connection string: postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "To connect manually:"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
