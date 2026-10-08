-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users (Instructors / App users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Students
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_identifier TEXT NOT NULL, -- e.g., Student ID number
    full_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, student_identifier)
);

-- 3. Writing Profiles (Fingerprints for a student)
CREATE TABLE writing_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    baseline_fingerprint JSONB NOT NULL,
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id)
);

-- 4. Submissions
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    assignment_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    character_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    extracted_text TEXT NOT NULL,
    embedding VECTOR(768), -- Uses pgvector for document-level embedding if needed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Analysis Results
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    linguistic_features JSONB,
    ai_signals JSONB,
    source_similarity JSONB,
    paraphrase_analysis JSONB,
    fingerprint_comparison JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(submission_id)
);

-- 7. Evidence
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    signal_name TEXT NOT NULL,
    score NUMERIC NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    supporting_metrics JSONB,
    reliability TEXT NOT NULL,
    contribution_to_risk NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Reports (Evidence Engine output & Gemini Explanation)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    overall_risk_score NUMERIC NOT NULL,
    risk_level TEXT NOT NULL,
    evidence_strength TEXT NOT NULL,
    confidence TEXT NOT NULL,
    safeguard_warnings JSONB,
    engine_conclusion TEXT NOT NULL,
    gemini_explanation JSONB, -- Stored ExplanationReport
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(submission_id)
);

-- Indexes for performance
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_submissions_student_id ON submissions(student_id);
CREATE INDEX idx_documents_submission_id ON documents(submission_id);
CREATE INDEX idx_evidence_submission_id ON evidence(submission_id);

-- Row Level Security (RLS) Design

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE writing_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 1. Users can only access their own user record
CREATE POLICY "Users can access their own record" ON users
    FOR ALL USING (auth.uid() = id);

-- 2. Instructors (Users) can only access students they manage
CREATE POLICY "Users can access their students" ON students
    FOR ALL USING (auth.uid() = user_id);

-- 3. Writing Profiles are accessible if the user owns the student
CREATE POLICY "Users can access writing profiles of their students" ON writing_profiles
    FOR ALL USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- 4. Submissions are accessible if the user owns the student
CREATE POLICY "Users can access submissions of their students" ON submissions
    FOR ALL USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- 5. Documents belong to submissions
CREATE POLICY "Users can access documents of their submissions" ON documents
    FOR ALL USING (
        submission_id IN (
            SELECT id FROM submissions WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );

-- 6. Analysis Results belong to submissions
CREATE POLICY "Users can access analysis results of their submissions" ON analysis_results
    FOR ALL USING (
        submission_id IN (
            SELECT id FROM submissions WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );

-- 7. Evidence belongs to submissions
CREATE POLICY "Users can access evidence of their submissions" ON evidence
    FOR ALL USING (
        submission_id IN (
            SELECT id FROM submissions WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );

-- 8. Reports belong to submissions
CREATE POLICY "Users can access reports of their submissions" ON reports
    FOR ALL USING (
        submission_id IN (
            SELECT id FROM submissions WHERE student_id IN (
                SELECT id FROM students WHERE user_id = auth.uid()
            )
        )
    );
