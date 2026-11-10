
def register_routes(app):

    from routes.employee_routes import employee_bp
    from routes.employee_profile_routes import profile_bp
    from routes.project_routes import project_bp
    from routes.task_routes import task_bp
    from routes.skill_routes import skill_bp
    from routes.employee_skill_routes import employee_skill_bp

    app.register_blueprint(employee_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(employee_skill_bp)
