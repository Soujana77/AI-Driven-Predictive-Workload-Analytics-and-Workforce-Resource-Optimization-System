
def register_routes(app):
    """
    Register all implemented API blueprints.
    """

    from routes.employee_routes import employee_bp

    app.register_blueprint(employee_bp)
