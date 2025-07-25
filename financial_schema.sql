-- Track all companies
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT
);

-- Track time periods: monthly, quarterly, YTD, LTM
CREATE TABLE periods (
    period_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    period_type TEXT CHECK (period_type IN ('Monthly', 'Quarterly', 'YTD', 'LTM')),
    fiscal_label TEXT,  -- e.g., 'Feb-25', 'Q1 2025'
    UNIQUE(company_id, start_date, end_date, period_type)
);

-- Raw values from files (actuals, budgets, variances)
CREATE TABLE datapoints (
    datapoint_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_id INT REFERENCES periods(period_id),
    metric TEXT CHECK (metric IN ('Revenue', 'Gross Profit', 'EBITDA')),
    value_type TEXT CHECK (value_type IN ('Actual', 'Budget', 'Variance (£)', 'Variance (%)')),
    raw_value NUMERIC(15, 2),
    source_file TEXT,
    page_number INT,
    extracted_from TEXT, -- e.g., 'Table: Monthly P&L'
    data_method TEXT CHECK (data_method IN ('Raw', 'Calculated', 'Corroborated')),
    version_tag TEXT,  -- hash or unique version string
    created_at TIMESTAMP DEFAULT now()
);

-- Log multiple sources for corroboration
CREATE TABLE datapoint_sources (
    source_id SERIAL PRIMARY KEY,
    datapoint_id INT REFERENCES datapoints(datapoint_id),
    file_name TEXT,
    page_number INT,
    extracted_from TEXT,
    captured_at TIMESTAMP DEFAULT now()
);

-- Store all calculations (MoM, QoQ, YoY, % growth, etc.)
CREATE TABLE calculations (
    calc_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_id INT REFERENCES periods(period_id),
    metric TEXT CHECK (metric IN ('Revenue', 'Gross Profit', 'EBITDA')),
    calculation_type TEXT,  -- e.g. 'YoY Growth', 'Variance to Budget', etc.
    base_value NUMERIC(15, 2),
    compare_value NUMERIC(15, 2),
    result NUMERIC(15, 2),
    result_pct NUMERIC(7, 2),
    calculation_formula TEXT,  -- e.g., "((A - B) / B) * 100"
    referenced_datapoints INT[],  -- array of datapoint_ids
    confidence_score NUMERIC(3, 2),  -- optional
    created_at TIMESTAMP DEFAULT now()
);

-- Weightings for analysis and scorecarding
CREATE TABLE weights (
    weight_id SERIAL PRIMARY KEY,
    metric TEXT CHECK (metric IN ('Revenue', 'Gross Profit', 'EBITDA')),
    calculation_type TEXT,
    default_weight NUMERIC(3,2),  -- e.g., 0.8
    source TEXT,  -- e.g., 'OpenAI GPT-4, July 2025'
    rationale TEXT
);

-- Scorecards generated from data + weights
CREATE TABLE scorecards (
    scorecard_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_id INT REFERENCES periods(period_id),
    metric TEXT,
    calculation_type TEXT,
    score NUMERIC(5,2),
    magnitude NUMERIC(15,2),
    weight_applied NUMERIC(3,2),
    notes TEXT
);

-- Checklist questions generated by triggers or manual review
CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_id INT REFERENCES periods(period_id),
    metric TEXT,
    question_text TEXT,
    answer_text TEXT,
    source_calc_id INT REFERENCES calculations(calc_id),
    severity_score NUMERIC(5,2),
    status TEXT CHECK (status IN ('New', 'Asked', 'Answered', 'Flagged')),
    created_at TIMESTAMP DEFAULT now()
);

-- File versioning and audit trail
CREATE TABLE file_log (
    file_id SERIAL PRIMARY KEY,
    file_name TEXT,
    file_hash TEXT,
    file_type TEXT CHECK (file_type IN ('xlsx', 'pdf')),
    ingest_status TEXT CHECK (ingest_status IN ('Processed', 'Skipped', 'Corrupted')),
    upload_date TIMESTAMP DEFAULT now(),
    notes TEXT
);
