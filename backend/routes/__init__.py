def register_routes(app):
    from routes.employee_routes import employee_bp
    from routes.employee_profile_routes import profile_bp

    app.register_blueprint(employee_bp)
    app.register_blueprint(profile_bp)