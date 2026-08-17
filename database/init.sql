-- ============================================================================
-- Agentic Job Hunter Database Schema
-- Phase 3: PostgreSQL Database
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PROFILE & CV MANAGEMENT (Phase 4)
-- ============================================================================

-- User profile information
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    location VARCHAR(255),
    education JSONB DEFAULT '[]',           -- Array of education entries
    experience JSONB DEFAULT '[]',           -- Array of experience entries
    skills JSONB DEFAULT '[]',               -- Array of skills
    portfolio VARCHAR(255),
    github VARCHAR(255),
    linkedin VARCHAR(255),
    salary_expectation INT,                  -- Annual salary in USD/equivalent
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Multiple CVs per user
CREATE TABLE cvs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    category VARCHAR(100),                   -- e.g., "ML/AI", "DevOps", "Backend", "General"
    target_roles JSONB DEFAULT '[]',         -- Array of target roles
    skills JSONB DEFAULT '[]',               -- Array of skills
    file_path VARCHAR(500) NOT NULL,         -- Path to stored CV file
    file_size INT,                           -- File size in bytes
    content_hash VARCHAR(64),                -- SHA-256 hash for duplicate detection
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_cv_filename UNIQUE(profile_id, filename)
);

-- ============================================================================
-- COMPANY & JOB SOURCE MANAGEMENT (Phase 5, 6, 7)
-- ============================================================================

-- Companies
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    website VARCHAR(500),
    career_page_url VARCHAR(500),
    logo_url VARCHAR(500),
    description TEXT,
    industry VARCHAR(100),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Job sources (abstract the source type)
CREATE TABLE job_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,       -- 'career_page', 'bdjobs', 'email', 'linkedin'
    source_url VARCHAR(500),                 -- URL to fetch jobs from
    api_endpoint VARCHAR(500),               -- If applicable
    extraction_strategy VARCHAR(100),        -- 'html', 'json', 'rss', 'api', 'sitemap'
    auth_method VARCHAR(50),                 -- 'none', 'api_key', 'oauth'
    auth_config JSONB DEFAULT '{}',          -- Store encrypted auth details
    polling_interval_hours INT DEFAULT 24,  -- How often to check for new jobs
    last_polled_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- JOB MANAGEMENT (Phase 8, 9)
-- ============================================================================

-- Jobs (normalized structure from all sources)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES job_sources(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    job_type VARCHAR(50),                    -- 'Full-time', 'Part-time', 'Contract', 'Internship'
    remote_type VARCHAR(50),                 -- 'remote', 'on-site', 'hybrid'
    salary_min INT,
    salary_max INT,
    currency VARCHAR(10) DEFAULT 'USD',
    experience_required INT,                 -- Years
    experience_level VARCHAR(50),            -- 'Entry', 'Mid', 'Senior', 'Lead'
    requirements JSONB DEFAULT '[]',         -- Array of required skills/qualifications
    nice_to_have JSONB DEFAULT '[]',         -- Array of nice-to-have skills
    application_url VARCHAR(500),
    posted_at TIMESTAMP,
    expires_at TIMESTAMP,
    normalized_hash VARCHAR(64),             -- hash(company + title + url) for deduplication
    is_duplicate BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_normalized_job UNIQUE(company_id, title, application_url)
);

-- ============================================================================
-- PREFERENCE FILTERING (Phase 9)
-- ============================================================================

-- User preferences for filtering
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    -- Location preferences
    preferred_locations JSONB DEFAULT '[]',
    exclude_locations JSONB DEFAULT '[]',
    allow_remote BOOLEAN DEFAULT true,
    allow_hybrid BOOLEAN DEFAULT true,
    allow_onsite BOOLEAN DEFAULT true,
    
    -- Experience preferences
    min_experience_years INT DEFAULT 0,
    max_experience_years INT DEFAULT 100,
    
    -- Job type preferences
    preferred_job_types JSONB DEFAULT '["Full-time"]',
    
    -- Salary preferences
    min_salary INT,
    max_salary INT,
    
    -- Keywords and skills
    required_keywords JSONB DEFAULT '[]',
    excluded_keywords JSONB DEFAULT '[]',
    
    -- Matching threshold
    min_match_score INT DEFAULT 70,         -- Minimum AI match score to proceed
    
    -- Companies
    preferred_companies JSONB DEFAULT '[]',
    excluded_companies JSONB DEFAULT '[]',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_preference_per_profile UNIQUE(profile_id)
);

-- ============================================================================
-- AI MATCHING (Phase 10, 11)
-- ============================================================================

-- Job matches (Gemini evaluation)
CREATE TABLE job_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    selected_cv_id UUID REFERENCES cvs(id) ON DELETE SET NULL,
    
    -- Match scoring
    match_score INT,                         -- 0-100
    recommendation VARCHAR(50),              -- 'APPLY', 'MAYBE', 'SKIP'
    matched_skills JSONB DEFAULT '[]',
    missing_skills JSONB DEFAULT '[]',
    experience_match BOOLEAN,
    reason TEXT,
    
    -- AI evaluation metadata
    ai_evaluation JSONB DEFAULT '{}',       -- Full response from Gemini
    evaluated_at TIMESTAMP,
    
    -- State
    status VARCHAR(50) DEFAULT 'DISCOVERED', -- See Phase 13 state machine
    notified_at TIMESTAMP,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT unique_match_per_job_profile UNIQUE(job_id, profile_id)
);

-- ============================================================================
-- APPLICATION MANAGEMENT (Phase 13, 14, 15, 16)
-- ============================================================================

-- Application states tracking
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_match_id UUID NOT NULL REFERENCES job_matches(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE RESTRICT,
    
    -- State machine
    status VARCHAR(100) DEFAULT 'DISCOVERED',
    -- Possible states: DISCOVERED, MATCHED, SHORTLISTED, AWAITING_APPROVAL, APPROVED,
    --                  PREPARING_APPLICATION, FORM_FILLING, WAITING_FOR_USER,
    --                  READY_TO_SUBMIT, SUBMITTED, REJECTED, FAILED,
    --                  NEEDS_MANUAL_INTERVENTION
    
    -- User approvals
    user_approved BOOLEAN DEFAULT false,
    approved_at TIMESTAMP,
    approval_notes TEXT,
    
    -- Form filling tracking
    form_url VARCHAR(500),
    form_data JSONB DEFAULT '{}',           -- Filled form data
    unknown_fields JSONB DEFAULT '[]',      -- Fields that needed LLM help
    
    -- Submission
    submitted_at TIMESTAMP,
    submission_error TEXT,
    
    -- Reliability (Phase 21)
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    last_error TEXT,
    last_error_at TIMESTAMP,
    screenshot_path VARCHAR(500),           -- Screenshot when failed
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Application form fields (flexible schema for unpredictable fields)
CREATE TABLE application_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    -- Field metadata
    field_name VARCHAR(255) NOT NULL,
    field_type VARCHAR(50),                  -- 'text', 'email', 'phone', 'number', 'date', 'boolean', 'select', 'textarea', etc.
    field_label TEXT,
    field_placeholder VARCHAR(255),
    
    -- Value and confidence
    answer TEXT,
    answer_type VARCHAR(50),                 -- 'profile_field', 'cv_field', 'derived', 'manual', 'ai_generated'
    ai_field_type VARCHAR(100),              -- e.g., 'current_salary', 'desired_salary', 'availability_date'
    ai_confidence FLOAT DEFAULT 0,           -- 0.0 to 1.0
    
    -- Status
    is_filled BOOLEAN DEFAULT false,
    is_required BOOLEAN DEFAULT false,
    requires_user_confirmation BOOLEAN DEFAULT false,
    user_confirmed BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- APPLICATION TRACKING (Phase 19)
-- ============================================================================

-- Application tracking and outcomes
CREATE TABLE application_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL UNIQUE REFERENCES applications(id) ON DELETE CASCADE,
    
    -- Tracking info
    company_name VARCHAR(255),
    position VARCHAR(255),
    application_url VARCHAR(500),
    cv_used VARCHAR(255),
    applied_at TIMESTAMP,
    
    -- Status tracking
    current_status VARCHAR(100),             -- 'APPLIED', 'REJECTED', 'INTERVIEW', 'TECHNICAL_INTERVIEW', 'OFFER', 'WITHDRAWN'
    status_updated_at TIMESTAMP,
    
    -- Interview tracking
    interview_count INT DEFAULT 0,
    interview_dates JSONB DEFAULT '[]',
    interview_notes JSONB DEFAULT '[]',
    
    -- Outcome
    outcome VARCHAR(50),                     -- 'PENDING', 'REJECTED', 'OFFER', 'WITHDRAWN'
    offer_details JSONB DEFAULT '{}',
    rejection_reason TEXT,
    
    -- Notes and attachments
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- NOTIFICATIONS (Phase 12)
-- ============================================================================

-- Notification tracking
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    job_match_id UUID REFERENCES job_matches(id) ON DELETE SET NULL,
    
    -- Notification details
    notification_type VARCHAR(50),           -- 'job_match', 'approval_needed', 'submission_failed', etc.
    title VARCHAR(255),
    message TEXT,
    
    -- Delivery
    delivery_channel VARCHAR(50) DEFAULT 'telegram',  -- 'telegram', 'email', 'sms'
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    delivery_status VARCHAR(50),             -- 'pending', 'sent', 'failed'
    delivery_error TEXT,
    
    -- User interaction
    action_required BOOLEAN DEFAULT false,
    action_type VARCHAR(100),                -- 'approve', 'reject', 'modify'
    user_action TEXT,
    user_action_at TIMESTAMP,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- LOGGING & AUDIT (Phase 21)
-- ============================================================================

-- Application logs for reliability and debugging
CREATE TABLE application_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
    
    -- Log details
    log_level VARCHAR(20),                   -- 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'
    log_source VARCHAR(100),                 -- 'playwright', 'n8n', 'api', 'gemini', etc.
    log_message TEXT NOT NULL,
    error_type VARCHAR(100),
    error_details JSONB DEFAULT '{}',
    
    -- Stack trace and context
    stack_trace TEXT,
    context JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail for all state changes
CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50),                 -- 'application', 'job_match', 'profile', etc.
    entity_id UUID NOT NULL,
    
    -- Change details
    action VARCHAR(50),                      -- 'create', 'update', 'delete', 'submit'
    old_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    changed_fields TEXT[],
    
    -- Context
    changed_by VARCHAR(100),
    reason TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Jobs
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_source_id ON jobs(source_id);
CREATE INDEX idx_jobs_normalized_hash ON jobs(normalized_hash);
CREATE INDEX idx_jobs_is_active ON jobs(is_active);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);

-- Job Matches
CREATE INDEX idx_job_matches_job_id ON job_matches(job_id);
CREATE INDEX idx_job_matches_profile_id ON job_matches(profile_id);
CREATE INDEX idx_job_matches_status ON job_matches(status);
CREATE INDEX idx_job_matches_match_score ON job_matches(match_score DESC);
CREATE INDEX idx_job_matches_created_at ON job_matches(created_at DESC);

-- Applications
CREATE INDEX idx_applications_job_match_id ON applications(job_match_id);
CREATE INDEX idx_applications_profile_id ON applications(profile_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created_at ON applications(created_at DESC);

-- CVs
CREATE INDEX idx_cvs_profile_id ON cvs(profile_id);
CREATE INDEX idx_cvs_is_active ON cvs(is_active);

-- Notifications
CREATE INDEX idx_notifications_profile_id ON notifications(profile_id);
CREATE INDEX idx_notifications_delivery_status ON notifications(delivery_status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Application Fields
CREATE INDEX idx_application_fields_application_id ON application_fields(application_id);

-- Application Logs
CREATE INDEX idx_application_logs_application_id ON application_logs(application_id);
CREATE INDEX idx_application_logs_log_level ON application_logs(log_level);
CREATE INDEX idx_application_logs_created_at ON application_logs(created_at DESC);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active jobs for the profile
CREATE VIEW vw_active_jobs_for_user AS
SELECT 
    j.id,
    j.title,
    c.name as company,
    j.location,
    j.job_type,
    j.remote_type,
    j.salary_min,
    j.salary_max,
    j.posted_at,
    j.created_at
FROM jobs j
JOIN companies c ON j.company_id = c.id
WHERE j.is_active = true
  AND j.is_duplicate = false
ORDER BY j.posted_at DESC;

-- Top matches requiring user action
CREATE VIEW vw_awaiting_user_action AS
SELECT 
    jm.id as match_id,
    a.id as application_id,
    j.title,
    c.name as company,
    jm.match_score,
    jm.recommendation,
    a.status,
    n.notification_type
FROM job_matches jm
LEFT JOIN applications a ON jm.id = a.job_match_id
LEFT JOIN jobs j ON jm.job_id = j.id
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN notifications n ON jm.id = n.job_match_id
WHERE jm.status = 'AWAITING_APPROVAL'
  AND a.user_approved = false
ORDER BY jm.match_score DESC;

-- Application summary
CREATE VIEW vw_application_summary AS
SELECT 
    p.name,
    c.name as company,
    j.title,
    a.status,
    a.created_at,
    a.submitted_at,
    cv.category as cv_used
FROM applications a
JOIN job_matches jm ON a.job_match_id = jm.id
JOIN jobs j ON a.job_id = j.id
JOIN companies c ON j.company_id = c.id
JOIN profiles p ON a.profile_id = p.id
JOIN cvs cv ON a.cv_id = cv.id
ORDER BY a.created_at DESC;

-- ============================================================================
-- TRIGGERS FOR AUDIT TRAIL
-- ============================================================================

-- Function to track changes
CREATE OR REPLACE FUNCTION track_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_trail (entity_type, entity_id, action, old_values, new_values, changed_fields, changed_by)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        to_jsonb(OLD),
        to_jsonb(NEW),
        ARRAY(SELECT key FROM jsonb_each(to_jsonb(NEW) - to_jsonb(OLD))),
        COALESCE(current_user, 'system')
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Track changes to applications
CREATE TRIGGER trg_applications_audit
AFTER INSERT OR UPDATE ON applications
FOR EACH ROW EXECUTE FUNCTION track_changes();

-- Track changes to job_matches
CREATE TRIGGER trg_job_matches_audit
AFTER INSERT OR UPDATE ON job_matches
FOR EACH ROW EXECUTE FUNCTION track_changes();

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Example profile
INSERT INTO profiles (name, email, phone, location, salary_expectation, github, linkedin)
VALUES (
    'Job Seeker',
    'jobseeker@example.com',
    '+1234567890',
    'New York, USA',
    120000,
    'https://github.com/jobseeker',
    'https://linkedin.com/in/jobseeker'
) ON CONFLICT (email) DO NOTHING;

-- Example company
INSERT INTO companies (name, website, career_page_url, industry)
VALUES (
    'Example Tech Company',
    'https://exampletech.com',
    'https://exampletech.com/careers',
    'Technology'
) ON CONFLICT (name) DO NOTHING;

-- Grant appropriate permissions (adjust as needed)
-- GRANT CONNECT ON DATABASE job_agent TO jobagent;
-- GRANT USAGE ON SCHEMA public TO jobagent;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO jobagent;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO jobagent;

COMMIT;
