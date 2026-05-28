def register_blueprints(app):
    from app.routes.projects import projects_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
