"""Tests for the project-material association service."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Material, MaterialCategory, Merchant
from app.services import project_material_service


def setup_app():
    """Create app with in-memory DB and seed required reference data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    merchant = Merchant(name="Home Depot")
    db.session.add_all([cat, merchant])
    db.session.commit()

    material = Material(name="2x4x8 Stud", default_price=4.00, category_id=cat.id)
    db.session.add(material)
    db.session.commit()

    project = Project(name="Kitchen Remodel", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project, material, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_add_material_to_project():
    app, ctx, project, material, merchant = setup_app()
    try:
        pm = project_material_service.add_material_to_project(
            project_id=project.id,
            material_id=material.id,
            quantity=10,
            estimated_unit_price=4.00,
            actual_unit_price=3.75,
            unit_of_measure="each",
            merchant_id=merchant.id,
            purchased_on="2026-05-20",
            notes="Bought on sale",
        )
        assert pm.id is not None
        assert pm.project_id == project.id
        assert pm.material_id == material.id
        assert pm.quantity == 10
        assert float(pm.estimated_unit_price) == 4.00
        assert float(pm.actual_unit_price) == 3.75
        assert pm.unit_of_measure == "each"
        assert pm.merchant_id == merchant.id
        assert pm.purchased_on.strftime("%Y-%m-%d") == "2026-05-20"
        assert pm.notes == "Bought on sale"
        print("PASS: test_add_material_to_project")
    finally:
        teardown(ctx)


def test_add_material_validation():
    app, ctx, project, material, merchant = setup_app()
    try:
        # Quantity <= 0
        try:
            project_material_service.add_material_to_project(
                project_id=project.id, material_id=material.id, quantity=0)
            assert False
        except ValueError as e:
            assert "greater than 0" in str(e)

        # Negative price
        try:
            project_material_service.add_material_to_project(
                project_id=project.id, material_id=material.id,
                quantity=1, estimated_unit_price=-5)
            assert False
        except ValueError as e:
            assert ">= 0" in str(e)

        # Non-existent project
        try:
            project_material_service.add_material_to_project(
                project_id=9999, material_id=material.id, quantity=1)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        # Non-existent material
        try:
            project_material_service.add_material_to_project(
                project_id=project.id, material_id=9999, quantity=1)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        # Completed project
        project.status = "completed"
        db.session.commit()
        try:
            project_material_service.add_material_to_project(
                project_id=project.id, material_id=material.id, quantity=1)
            assert False
        except ValueError as e:
            assert "completed" in str(e).lower()

        print("PASS: test_add_material_validation")
    finally:
        teardown(ctx)


def test_list_project_materials():
    app, ctx, project, material, merchant = setup_app()
    try:
        project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id, quantity=5)
        project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id, quantity=3)

        results = project_material_service.list_project_materials(project.id)
        assert len(results) == 2

        # Non-existent project
        try:
            project_material_service.list_project_materials(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_list_project_materials")
    finally:
        teardown(ctx)


def test_get_project_material():
    app, ctx, project, material, merchant = setup_app()
    try:
        pm = project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id, quantity=2)

        fetched = project_material_service.get_project_material(pm.id)
        assert fetched is not None
        assert fetched.quantity == 2

        assert project_material_service.get_project_material(9999) is None
        print("PASS: test_get_project_material")
    finally:
        teardown(ctx)


def test_update_project_material():
    app, ctx, project, material, merchant = setup_app()
    try:
        pm = project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id,
            quantity=5, estimated_unit_price=4.00)

        updated = project_material_service.update_project_material(
            pm.id,
            quantity=10,
            actual_unit_price=3.50,
            unit_of_measure="board",
            notes="Updated",
        )
        assert updated.quantity == 10
        assert float(updated.actual_unit_price) == 3.50
        assert updated.unit_of_measure == "board"
        assert updated.notes == "Updated"

        print("PASS: test_update_project_material")
    finally:
        teardown(ctx)


def test_update_completed_project_rejected():
    app, ctx, project, material, merchant = setup_app()
    try:
        pm = project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id, quantity=1)

        project.status = "completed"
        db.session.commit()

        try:
            project_material_service.update_project_material(pm.id, quantity=5)
            assert False
        except ValueError as e:
            assert "completed" in str(e).lower()

        print("PASS: test_update_completed_project_rejected")
    finally:
        teardown(ctx)


def test_remove_material_from_project():
    app, ctx, project, material, merchant = setup_app()
    try:
        pm = project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id, quantity=1)
        pm_id = pm.id

        result = project_material_service.remove_material_from_project(pm_id)
        assert result is True
        assert project_material_service.get_project_material(pm_id) is None

        # Non-existent
        try:
            project_material_service.remove_material_from_project(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_remove_material_from_project")
    finally:
        teardown(ctx)


def test_totals_use_project_specific_prices():
    """Verify project totals use project-material prices, not catalog defaults."""
    app, ctx, project, material, merchant = setup_app()
    try:
        # Catalog default is $4.00, but project price is $5.00
        project_material_service.add_material_to_project(
            project_id=project.id, material_id=material.id,
            quantity=10, estimated_unit_price=5.00, actual_unit_price=4.50)

        # Refresh project to recalculate
        db.session.refresh(project)
        assert float(project.estimated_total) == 50.00  # 10 * 5.00
        assert float(project.actual_total) == 45.00     # 10 * 4.50
        assert float(project.variance) == -5.00         # under budget

        print("PASS: test_totals_use_project_specific_prices")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_add_material_to_project()
    test_add_material_validation()
    test_list_project_materials()
    test_get_project_material()
    test_update_project_material()
    test_update_completed_project_rejected()
    test_remove_material_from_project()
    test_totals_use_project_specific_prices()
    print("\nAll tests passed!")
