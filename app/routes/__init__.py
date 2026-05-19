def register_blueprints(app):
    from app.routes.projects import projects_bp
    app.register_blueprint(projects_bp)
