-- Congress.gov API Database Schema
-- Version: 1.0.0
-- Description: Initial schema for storing Congress.gov API data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Congress table
CREATE TABLE IF NOT EXISTS congress (
    id SERIAL PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    name VARCHAR(100),
    start_year INTEGER,
    end_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members table
CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    bioguide_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    suffix VARCHAR(20),
    nickname VARCHAR(100),
    party VARCHAR(50),
    state VARCHAR(2),
    district INTEGER,
    birth_year INTEGER,
    death_year INTEGER,
    terms JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    bill_type VARCHAR(10) NOT NULL,
    bill_number INTEGER NOT NULL,
    title TEXT,
    origin_chamber VARCHAR(20),
    origin_chamber_code VARCHAR(1),
    update_date DATE,
    update_date_including_text DATE,
    introduced_date DATE,
    constitution_authority_statement_text TEXT,
    policy_area JSONB,
    subjects JSONB,
    latest_action JSONB,
    sponsors JSONB,
    cosponsors_count INTEGER,
    committees JSONB,
    related_bills JSONB,
    actions JSONB,
    summaries JSONB,
    amendments JSONB,
    texts JSONB,
    titles JSONB,
    law_number VARCHAR(50),
    law_type VARCHAR(50),
    is_law BOOLEAN DEFAULT FALSE,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, bill_type, bill_number)
);

-- Committees table
CREATE TABLE IF NOT EXISTS committees (
    id SERIAL PRIMARY KEY,
    system_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    chamber VARCHAR(20),
    type VARCHAR(50),
    subcommittees JSONB,
    parent_committee_system_code VARCHAR(20),
    is_subcommittee BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Amendments table
CREATE TABLE IF NOT EXISTS amendments (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    amendment_type VARCHAR(10) NOT NULL,
    amendment_number INTEGER NOT NULL,
    bill_congress INTEGER,
    bill_type VARCHAR(10),
    bill_number INTEGER,
    purpose TEXT,
    description TEXT,
    chamber VARCHAR(20),
    amendment_to_amendment JSONB,
    sponsors JSONB,
    cosponsors JSONB,
    proposed_date DATE,
    submitted_date DATE,
    latest_action JSONB,
    actions JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, amendment_type, amendment_number)
);

-- Nominations table
CREATE TABLE IF NOT EXISTS nominations (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    nomination_number VARCHAR(20) NOT NULL,
    part_number VARCHAR(10),
    citation VARCHAR(100),
    description TEXT,
    received_date DATE,
    authority_date DATE,
    executive_calendar_number VARCHAR(20),
    organization VARCHAR(255),
    position_title VARCHAR(255),
    nominee_bioguide_id VARCHAR(20),
    latest_action JSONB,
    actions JSONB,
    committees JSONB,
    hearings JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, nomination_number, part_number)
);

-- Treaties table
CREATE TABLE IF NOT EXISTS treaties (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    treaty_number INTEGER NOT NULL,
    suffix VARCHAR(10),
    treaty_name VARCHAR(500),
    topic VARCHAR(255),
    country VARCHAR(100),
    transmitted_date DATE,
    in_force_date DATE,
    resolution_text TEXT,
    latest_action JSONB,
    actions JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, treaty_number, suffix)
);

-- Committee Reports table
CREATE TABLE IF NOT EXISTS committee_reports (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    report_type VARCHAR(10) NOT NULL,
    report_number INTEGER NOT NULL,
    part INTEGER,
    citation VARCHAR(100),
    title TEXT,
    chamber VARCHAR(20),
    report_date DATE,
    committees JSONB,
    associated_bills JSONB,
    associated_treaties JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, report_type, report_number, part)
);

-- Hearings table
CREATE TABLE IF NOT EXISTS hearings (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    chamber VARCHAR(20),
    jacket_number INTEGER NOT NULL,
    hearing_number VARCHAR(50),
    part INTEGER,
    citation VARCHAR(100),
    title TEXT,
    date DATE,
    committees JSONB,
    associated_bills JSONB,
    formats JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, chamber, jacket_number, part)
);

-- Congressional Record table
CREATE TABLE IF NOT EXISTS congressional_record (
    id SERIAL PRIMARY KEY,
    congress INTEGER NOT NULL,
    session INTEGER NOT NULL,
    issue_number INTEGER NOT NULL,
    volume_number INTEGER NOT NULL,
    publication_date DATE,
    sections JSONB,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(congress, session, issue_number)
);

-- API Sync Log table
CREATE TABLE IF NOT EXISTS api_sync_log (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    sync_type VARCHAR(50), -- 'full', 'incremental', 'single'
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20), -- 'running', 'completed', 'failed'
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_bills_congress ON bills(congress);
CREATE INDEX idx_bills_type ON bills(bill_type);
CREATE INDEX idx_bills_update_date ON bills(update_date DESC);
CREATE INDEX idx_bills_is_law ON bills(is_law);
CREATE INDEX idx_bills_origin_chamber ON bills(origin_chamber);

CREATE INDEX idx_members_bioguide ON members(bioguide_id);
CREATE INDEX idx_members_party ON members(party);
CREATE INDEX idx_members_state ON members(state);

CREATE INDEX idx_amendments_congress ON amendments(congress);
CREATE INDEX idx_amendments_bill ON amendments(bill_congress, bill_type, bill_number);

CREATE INDEX idx_committees_chamber ON committees(chamber);
CREATE INDEX idx_committees_type ON committees(type);

CREATE INDEX idx_nominations_congress ON nominations(congress);
CREATE INDEX idx_nominations_nominee ON nominations(nominee_bioguide_id);

CREATE INDEX idx_treaties_congress ON treaties(congress);
CREATE INDEX idx_treaties_country ON treaties(country);

CREATE INDEX idx_committee_reports_congress ON committee_reports(congress);
CREATE INDEX idx_hearings_congress ON hearings(congress);
CREATE INDEX idx_congressional_record_date ON congressional_record(publication_date DESC);

CREATE INDEX idx_api_sync_log_endpoint ON api_sync_log(endpoint);
CREATE INDEX idx_api_sync_log_started ON api_sync_log(started_at DESC);

-- Create full-text search indexes
CREATE INDEX idx_bills_title_fts ON bills USING gin(to_tsvector('english', title));
CREATE INDEX idx_bills_raw_data_gin ON bills USING gin(raw_data);
CREATE INDEX idx_members_names_fts ON members USING gin(to_tsvector('english', first_name || ' ' || last_name));

-- Add trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_congress_updated_at BEFORE UPDATE ON congress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON members FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_committees_updated_at BEFORE UPDATE ON committees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_amendments_updated_at BEFORE UPDATE ON amendments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nominations_updated_at BEFORE UPDATE ON nominations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_treaties_updated_at BEFORE UPDATE ON treaties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_committee_reports_updated_at BEFORE UPDATE ON committee_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hearings_updated_at BEFORE UPDATE ON hearings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_congressional_record_updated_at BEFORE UPDATE ON congressional_record FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
