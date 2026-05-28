"""Service layer for project cost calculations.

All cost totals are computed dynamically from project_materials and project_tools.
No totals are stored in the database.
"""
from app.models import Project, ProjectMaterial, ProjectTool


def get_project_estimated_total(project_id):
    """Calculate the estimated total cost for a project.

    Formula:
        SUM(project_materials.quantity * project_materials.estimated_unit_price)
        + SUM(project_tools.quantity * project_tools.estimated_unit_price WHERE already_owned = false)

    Args:
        project_id: Integer project primary key.

    Returns:
        Float total estimated cost.

    Raises:
        ValueError: If project not found.
    """
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    material_est = _sum_material_estimated(project.project_materials)
    tool_est = _sum_tool_estimated(project.project_tools)
    return material_est + tool_est


def get_project_actual_total(project_id):
    """Calculate the actual total cost for a project.

    Formula:
        SUM(project_materials.quantity * project_materials.actual_unit_price)
        + SUM(project_tools.quantity * project_tools.actual_unit_price WHERE already_owned = false)

    NULL actual_unit_price contributes $0.
    Tools with already_owned = true contribute $0.

    Args:
        project_id: Integer project primary key.

    Returns:
        Float total actual cost.

    Raises:
        ValueError: If project not found.
    """
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    material_act = _sum_material_actual(project.project_materials)
    tool_act = _sum_tool_actual(project.project_tools)
    return material_act + tool_act


def get_project_variance(project_id):
    """Calculate variance for a project.

    Formula: actual_total - estimated_total
    Positive = over budget, Negative = under budget.

    Args:
        project_id: Integer project primary key.

    Returns:
        Float variance amount.

    Raises:
        ValueError: If project not found.
    """
    estimated = get_project_estimated_total(project_id)
    actual = get_project_actual_total(project_id)
    return actual - estimated


def get_project_cost_summary(project_id):
    """Get a full cost summary for a project in one call.

    Args:
        project_id: Integer project primary key.

    Returns:
        Dict with keys: estimated_total, actual_total, variance,
        material_estimated, material_actual, tool_estimated, tool_actual.

    Raises:
        ValueError: If project not found.
    """
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    material_est = _sum_material_estimated(project.project_materials)
    material_act = _sum_material_actual(project.project_materials)
    tool_est = _sum_tool_estimated(project.project_tools)
    tool_act = _sum_tool_actual(project.project_tools)

    estimated_total = material_est + tool_est
    actual_total = material_act + tool_act

    return {
        "estimated_total": estimated_total,
        "actual_total": actual_total,
        "variance": actual_total - estimated_total,
        "material_estimated": material_est,
        "material_actual": material_act,
        "tool_estimated": tool_est,
        "tool_actual": tool_act,
    }


# --- Internal helpers ---

def _sum_material_estimated(project_materials):
    """Sum quantity * estimated_unit_price for all project materials."""
    return sum(
        pm.quantity * float(pm.estimated_unit_price or 0)
        for pm in project_materials
    )


def _sum_material_actual(project_materials):
    """Sum quantity * actual_unit_price for all project materials."""
    return sum(
        pm.quantity * float(pm.actual_unit_price or 0)
        for pm in project_materials
    )


def _sum_tool_estimated(project_tools):
    """Sum quantity * estimated_unit_price for purchased tools only."""
    return sum(
        pt.quantity * float(pt.estimated_unit_price or 0)
        for pt in project_tools
        if not pt.already_owned
    )


def _sum_tool_actual(project_tools):
    """Sum quantity * actual_unit_price for purchased tools only."""
    return sum(
        pt.quantity * float(pt.actual_unit_price or 0)
        for pt in project_tools
        if not pt.already_owned
    )


# ============================================================
# Global Spend Summaries
# ============================================================

def get_global_material_spend():
    """Calculate all-time actual material spend across all projects.

    Formula:
        SUM(project_materials.quantity * project_materials.actual_unit_price)
        across ALL project_materials rows.

    Null handling:
        - Rows where actual_unit_price is NULL contribute $0.
        - Rows where actual_unit_price is 0 contribute $0 (zero-price rows are included
          in the sum but produce no spend).

    Returns:
        Float total actual material spend.
    """
    all_pm = ProjectMaterial.query.all()
    return sum(
        pm.quantity * float(pm.actual_unit_price or 0)
        for pm in all_pm
    )


def get_global_tool_spend():
    """Calculate all-time actual tool spend across all projects (purchased only).

    Formula:
        SUM(project_tools.quantity * project_tools.actual_unit_price)
        WHERE already_owned = false, across ALL project_tools rows.

    Null handling:
        - Rows where actual_unit_price is NULL contribute $0.
        - Rows where already_owned = true are excluded entirely.
        - Rows where actual_unit_price is 0 contribute $0 (zero-price rows are included
          but produce no spend).

    Returns:
        Float total actual tool spend (purchased tools only).
    """
    all_pt = ProjectTool.query.all()
    return sum(
        pt.quantity * float(pt.actual_unit_price or 0)
        for pt in all_pt
        if not pt.already_owned
    )


def get_global_spend_summary():
    """Get a full global spend summary in one call.

    Returns:
        Dict with keys:
            material_spend: all-time actual material spend
            tool_spend: all-time actual purchased tool spend
            total_spend: material_spend + tool_spend
    """
    material_spend = get_global_material_spend()
    tool_spend = get_global_tool_spend()
    return {
        "material_spend": material_spend,
        "tool_spend": tool_spend,
        "total_spend": material_spend + tool_spend,
    }
