CREATE TABLE IF NOT EXISTS managed_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(200) NOT NULL,
    description TEXT,

    start_date DATE,
    deadline DATE,

    priority VARCHAR(20) NOT NULL DEFAULT 'Medium'
        CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),

    status VARCHAR(30) NOT NULL DEFAULT 'Planning'
        CHECK (status IN ('Planning', 'Active', 'Completed', 'On Hold')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS managed_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id UUID NOT NULL
        REFERENCES managed_projects(id) ON DELETE CASCADE,

    title VARCHAR(200) NOT NULL,
    description TEXT,

    assigned_employee_id UUID
        REFERENCES employee_profiles(employee_id) ON DELETE SET NULL,

    estimated_hours NUMERIC(7,2) DEFAULT 0
        CHECK (estimated_hours >= 0),

    due_date DATE,

    priority VARCHAR(20) NOT NULL DEFAULT 'Medium'
        CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),

    status VARCHAR(30) NOT NULL DEFAULT 'To Do'
        CHECK (status IN ('To Do', 'In Progress', 'Completed', 'Blocked')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);