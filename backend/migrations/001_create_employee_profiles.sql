CREATE TABLE IF NOT EXISTS employee_profiles (
    employee_id UUID PRIMARY KEY
        REFERENCES employees(id) ON DELETE CASCADE,

    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE,
    job_title VARCHAR(100),
    department VARCHAR(100),

    experience_years NUMERIC(4,1)
        CHECK (experience_years >= 0),

    weekly_capacity_hours NUMERIC(5,2)
        NOT NULL DEFAULT 40
        CHECK (weekly_capacity_hours > 0),

    availability_status VARCHAR(30)
        NOT NULL DEFAULT 'Available'
        CHECK (
            availability_status IN (
                'Available',
                'Busy',
                'On Leave',
                'Inactive'
            )
        ),

    created_at TIMESTAMP WITH TIME ZONE
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE
        DEFAULT CURRENT_TIMESTAMP
);