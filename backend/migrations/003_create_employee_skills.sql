
-- Migration 003: Employee Skills Management

-- 1. Master catalogue of company skills
CREATE TABLE IF NOT EXISTS skills (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,

    description TEXT,

    created_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Prevent duplicate skill names, including different letter cases.
CREATE UNIQUE INDEX IF NOT EXISTS uq_skills_name_lower
ON skills (LOWER(name));


-- 2. Employee-to-skill relationship table
CREATE TABLE IF NOT EXISTS employee_skills (

    employee_id UUID NOT NULL
        REFERENCES employee_profiles(employee_id)
        ON DELETE CASCADE,

    skill_id UUID NOT NULL
        REFERENCES skills(id)
        ON DELETE CASCADE,

    proficiency_level VARCHAR(20) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_employee_skills
        PRIMARY KEY (employee_id, skill_id),

    CONSTRAINT chk_employee_skill_proficiency
        CHECK (
            proficiency_level IN (
                'Beginner',
                'Intermediate',
                'Advanced',
                'Expert'
            )
        )
);


-- 3. Index for finding employees who possess a particular skill.
CREATE INDEX IF NOT EXISTS idx_employee_skills_skill_id
ON employee_skills(skill_id);
