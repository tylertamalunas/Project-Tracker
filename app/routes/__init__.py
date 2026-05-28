from flask import redirect


def register_blueprints(app):
    from app.routes.projects import projects_bp
    app.register_blueprint(projects_bp)

    @app.route("/")
    def index():
        """Redirect root to projects list until dashboard is built."""
        return redirect("/projects")
