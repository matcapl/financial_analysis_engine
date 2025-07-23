CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE periods (
    id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    fiscal_period TEXT,          -- e.g., 'Q1 2024'
    frequency TEXT CHECK (frequency IN ('Monthly', 'Quarterly')),
    UNIQUE(start_date, end_date, frequency)
);

CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    period_id INT REFERENCES periods(id),
    metric TEXT,                -- e.g., 'Revenue', 'Gross Profit'
    value_type TEXT CHECK (value_type IN ('Actual', 'Budget', 'Prior')),
    frequency TEXT CHECK (frequency IN ('Monthly', 'Quarterly')),
    UNIQUE(company_id, period_id, metric, value_type, frequency)
);

CREATE TABLE financial_metric_versions (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES financial_metrics(id),
    version_number INT NOT NULL,
    raw_value NUMERIC(15, 2),
    source_id INT REFERENCES data_sources(id),
    ingestion_timestamp TIMESTAMP DEFAULT NOW(),
    note TEXT,
    is_current BOOLEAN DEFAULT FALSE
);

CREATE TABLE metric_change_logs (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES financial_metrics(id),
    old_version INT,
    new_version INT,
    old_value NUMERIC(15, 2),
    new_value NUMERIC(15, 2),
    delta NUMERIC(15, 2),
    flagged_as_conflict BOOLEAN DEFAULT FALSE,
    detected_on TIMESTAMP DEFAULT NOW(),
    note TEXT
);

CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    page_number INT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    uploader TEXT,
    notes TEXT
);

CREATE TABLE derived_metrics (
    id SERIAL PRIMARY KEY,
    base_metric TEXT,                   -- e.g., 'Revenue'
    calculation_type TEXT,              -- e.g., 'Growth vs Prior Period'
    company_id INT REFERENCES companies(id),
    period_id INT REFERENCES periods(id),
    calculated_value NUMERIC(15, 4),
    source_metric_ids INT[],           -- Optional: raw metric linkages
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE metric_weights (
    id SERIAL PRIMARY KEY,
    metric TEXT UNIQUE,
    default_weight NUMERIC(4, 2) DEFAULT 0.5,
    notes TEXT
);

CREATE TABLE live_questions (
    id SERIAL PRIMARY KEY,
    derived_metric_id INT REFERENCES derived_metrics(id),
    template_id INT,                           -- Optional for future use
    weight NUMERIC(4,2),
    scorecard JSONB,
    rank_score NUMERIC(6,2),
    rank_position INT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'retired')),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE question_logs (
    id SERIAL PRIMARY KEY,
    live_question_id INT REFERENCES live_questions(id),
    change_type TEXT,                       -- 'question_created', 'rank_updated', etc.
    changed_by TEXT,
    old_value TEXT,
    new_value TEXT,
    change_note TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE question_templates (
    id SERIAL PRIMARY KEY,
    metric TEXT,
    calculation_type TEXT,
    base_question TEXT,
    trigger_threshold NUMERIC(5, 2),
    trigger_operator TEXT CHECK (trigger_operator IN ('<', '>', '=', '<=', '>=')),
    default_weight NUMERIC(4,2)
);

