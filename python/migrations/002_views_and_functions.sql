-- Congress.gov API Database Views and Functions
-- Version: 1.0.0
-- Description: Analytical views and helper functions

-- View: Recent Bills
CREATE OR REPLACE VIEW recent_bills AS
SELECT 
    b.id,
    b.congress,
    b.bill_type,
    b.bill_number,
    b.title,
    b.introduced_date,
    b.update_date,
    b.origin_chamber,
    b.is_law,
    b.cosponsors_count,
    b.latest_action->>'actionDate' as latest_action_date,
    b.latest_action->>'text' as latest_action_text
FROM bills b
WHERE b.update_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY b.update_date DESC;

-- View: Bills by Status
CREATE OR REPLACE VIEW bills_by_status AS
SELECT 
    congress,
    origin_chamber,
    is_law,
    COUNT(*) as bill_count,
    AVG(cosponsors_count) as avg_cosponsors
FROM bills
GROUP BY congress, origin_chamber, is_law;

-- View: Member Activity Summary
CREATE OR REPLACE VIEW member_activity_summary AS
SELECT 
    m.bioguide_id,
    m.first_name || ' ' || m.last_name as full_name,
    m.party,
    m.state,
    COUNT(DISTINCT b.id) as bills_sponsored,
    AVG(b.cosponsors_count) as avg_cosponsors_per_bill
FROM members m
LEFT JOIN bills b ON b.sponsors->0->>'bioguideId' = m.bioguide_id
GROUP BY m.bioguide_id, m.first_name, m.last_name, m.party, m.state;

-- View: Committee Activity
CREATE OR REPLACE VIEW committee_activity AS
SELECT 
    c.system_code,
    c.name,
    c.chamber,
    COUNT(DISTINCT b.id) as bills_referred,
    COUNT(DISTINCT cr.id) as reports_issued
FROM committees c
LEFT JOIN bills b ON b.committees::text LIKE '%' || c.system_code || '%'
LEFT JOIN committee_reports cr ON cr.committees::text LIKE '%' || c.system_code || '%'
GROUP BY c.system_code, c.name, c.chamber;

-- View: Congressional Session Statistics
CREATE OR REPLACE VIEW session_statistics AS
SELECT 
    congress,
    COUNT(*) as total_bills,
    COUNT(*) FILTER (WHERE is_law = true) as laws_enacted,
    COUNT(*) FILTER (WHERE origin_chamber = 'House') as house_bills,
    COUNT(*) FILTER (WHERE origin_chamber = 'Senate') as senate_bills,
    COUNT(DISTINCT bill_type) as bill_types,
    MIN(introduced_date) as session_start,
    MAX(update_date) as last_update
FROM bills
GROUP BY congress
ORDER BY congress DESC;

-- Function: Get Bill Full Text
CREATE OR REPLACE FUNCTION get_bill_identifier(p_congress INTEGER, p_type VARCHAR, p_number INTEGER)
RETURNS VARCHAR AS $$
BEGIN
    RETURN CONCAT(p_congress, '-', p_type, p_number);
END;
$$ LANGUAGE plpgsql;

-- Function: Search Bills by Keyword
CREATE OR REPLACE FUNCTION search_bills(keyword TEXT)
RETURNS TABLE(
    id INTEGER,
    congress INTEGER,
    bill_type VARCHAR,
    bill_number INTEGER,
    title TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.id,
        b.congress,
        b.bill_type,
        b.bill_number,
        b.title,
        ts_rank(to_tsvector('english', b.title), plainto_tsquery('english', keyword)) as rank
    FROM bills b
    WHERE to_tsvector('english', b.title) @@ plainto_tsquery('english', keyword)
    ORDER BY rank DESC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

-- Function: Get Bills by Date Range
CREATE OR REPLACE FUNCTION get_bills_by_date_range(
    start_date DATE,
    end_date DATE,
    p_congress INTEGER DEFAULT NULL
)
RETURNS TABLE(
    id INTEGER,
    congress INTEGER,
    bill_type VARCHAR,
    bill_number INTEGER,
    title TEXT,
    introduced_date DATE,
    update_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.id,
        b.congress,
        b.bill_type,
        b.bill_number,
        b.title,
        b.introduced_date,
        b.update_date
    FROM bills b
    WHERE b.update_date BETWEEN start_date AND end_date
        AND (p_congress IS NULL OR b.congress = p_congress)
    ORDER BY b.update_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate Bill Progression Stats
CREATE OR REPLACE FUNCTION calculate_bill_progression_stats(p_congress INTEGER)
RETURNS TABLE(
    stage VARCHAR,
    count BIGINT,
    percentage NUMERIC
) AS $$
DECLARE
    total_bills BIGINT;
BEGIN
    SELECT COUNT(*) INTO total_bills FROM bills WHERE congress = p_congress;
    
    RETURN QUERY
    WITH bill_stages AS (
        SELECT 
            CASE 
                WHEN b.is_law THEN 'Became Law'
                WHEN b.latest_action->>'text' LIKE '%passed%' THEN 'Passed'
                WHEN b.latest_action->>'text' LIKE '%committee%' THEN 'In Committee'
                ELSE 'Introduced'
            END as stage,
            COUNT(*) as stage_count
        FROM bills b
        WHERE b.congress = p_congress
        GROUP BY stage
    )
    SELECT 
        bs.stage,
        bs.stage_count,
        ROUND((bs.stage_count::NUMERIC / total_bills) * 100, 2) as percentage
    FROM bill_stages bs
    ORDER BY bs.stage_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get Member Voting Pattern (placeholder for future expansion)
CREATE OR REPLACE FUNCTION get_member_statistics(p_bioguide_id VARCHAR)
RETURNS TABLE(
    bioguide_id VARCHAR,
    full_name VARCHAR,
    party VARCHAR,
    state VARCHAR,
    bills_sponsored BIGINT,
    bills_cosponsored BIGINT,
    amendments_sponsored BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.bioguide_id,
        m.first_name || ' ' || m.last_name as full_name,
        m.party,
        m.state,
        COUNT(DISTINCT b.id) as bills_sponsored,
        (
            SELECT COUNT(*)
            FROM bills b2
            WHERE b2.raw_data->'cosponsors' @> jsonb_build_array(jsonb_build_object('bioguideId', m.bioguide_id))
        ) as bills_cosponsored,
        COUNT(DISTINCT a.id) as amendments_sponsored
    FROM members m
    LEFT JOIN bills b ON b.sponsors->0->>'bioguideId' = m.bioguide_id
    LEFT JOIN amendments a ON a.sponsors->0->>'bioguideId' = m.bioguide_id
    WHERE m.bioguide_id = p_bioguide_id
    GROUP BY m.bioguide_id, m.first_name, m.last_name, m.party, m.state;
END;
$$ LANGUAGE plpgsql;

-- Materialized view for performance: Bill Trends
CREATE MATERIALIZED VIEW IF NOT EXISTS bill_trends AS
SELECT 
    congress,
    DATE_TRUNC('month', introduced_date) as month,
    bill_type,
    origin_chamber,
    COUNT(*) as bill_count,
    COUNT(*) FILTER (WHERE is_law = true) as laws_count,
    AVG(cosponsors_count) as avg_cosponsors
FROM bills
WHERE introduced_date IS NOT NULL
GROUP BY congress, DATE_TRUNC('month', introduced_date), bill_type, origin_chamber
ORDER BY congress DESC, month DESC;

CREATE INDEX idx_bill_trends_congress_month ON bill_trends(congress, month DESC);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_bill_trends()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY bill_trends;
END;
$$ LANGUAGE plpgsql;
