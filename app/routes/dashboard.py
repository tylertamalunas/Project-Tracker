"""Dashboard route — application overview with global spend summaries."""
from flask import Blueprint, render_template
from app.models import Project
from app.services import cost_service

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    """Render the dashboard with project counts and global spend metrics."""
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status="active").count()
    completed_projects = Project.query.filter_by(status="completed").count()

    # Global spend summaries
    spend = cost_service.get_global_spend_summary()

    # Recent projects (up to 5, active first, then planned)
    recent = Project.query.filter(
        Project.status.in_(["active", "planned"])
    ).order_by(Project.updated_at.desc()).limit(5).all()

    # Projects over budget (variance > 0)
    all_active = Project.query.filter(
        Project.status.in_(["active", "completed"])
    ).all()
    over_budget = [p for p in all_active if p.variance > 0]
    over_budget.sort(key=lambda p: p.variance, reverse=True)

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        material_spend=spend["material_spend"],
        tool_spend=spend["tool_spend"],
        total_spend=spend["total_spend"],
        recent_projects=recent,
        over_budget_projects=over_budget[:5],
    )
