def register_blueprints(app):
    from app.routes.projects import projects_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.materials import materials_bp
    from app.routes.tools import tools_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(tools_bp)
