"""Tests for the material service layer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import MaterialCategory, Merchant
from app.services import material_service


def setup_app():
    """Create app with in-memory DB and seed lookup data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    # Seed reference data
    cat = MaterialCategory(name="Lumber", description="Wood products")
    merchant = Merchant(name="Home Depot", website="https://homedepot.com")
    db.session.add_all([cat, merchant])
    db.session.commit()
    return app, ctx, cat, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_material():
    app, ctx, cat, merchant = setup_app()
    try:
        m = material_service.create_material(
            name="2x4x8 Stud",
            default_price=3.98,
            unit_of_measure="each",
            sku="SKU-2x4-8",
            brand="Generic",
            category_id=cat.id,
            merchant_id=merchant.id,
            notes="Standard framing lumber",
        )
        assert m.id is not None
        assert m.name == "2x4x8 Stud"
        assert float(m.default_price) == 3.98
        assert m.unit_of_measure == "each"
        assert m.sku == "SKU-2x4-8"
        assert m.brand == "Generic"
        assert m.category_id == cat.id
        assert m.merchant_id == merchant.id
        assert m.notes == "Standard framing lumber"
        assert m.is_active is True
        assert m.created_at is not None
        print("PASS: test_create_material")
    finally:
        teardown(ctx)


def test_create_material_validation():
    app, ctx, cat, merchant = setup_app()
    try:
        # Empty name
        try:
            material_service.create_material(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "name is required" in str(e)

        # Negative price
        try:
            material_service.create_material(name="Test", default_price=-1)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "must be >= 0" in str(e)

        # Invalid category
        try:
            material_service.create_material(name="Test", category_id=9999)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        # Invalid merchant
        try:
            material_service.create_material(name="Test", merchant_id=9999)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_create_material_validation")
    finally:
        teardown(ctx)


def test_list_materials():
    app, ctx, cat, merchant = setup_app()
    try:
        material_service.create_material(name="Active Item 1", is_active=True)
        material_service.create_material(name="Active Item 2", is_active=True)
        material_service.create_material(name="Inactive Item", is_active=False)

        # All
        all_mats = material_service.list_materials()
        assert len(all_mats) == 3

        # Active only
        active = material_service.list_materials(active_only=True)
        assert len(active) == 2
        assert all(m.is_active for m in active)

        # Inactive only
        inactive = material_service.list_materials(active_only=False)
        assert len(inactive) == 1
        assert not inactive[0].is_active

        print("PASS: test_list_materials")
    finally:
        teardown(ctx)


def test_list_materials_by_category():
    app, ctx, cat, merchant = setup_app()
    try:
        material_service.create_material(name="In Category", category_id=cat.id)
        material_service.create_material(name="No Category")

        filtered = material_service.list_materials(category_id=cat.id)
        assert len(filtered) == 1
        assert filtered[0].name == "In Category"

        print("PASS: test_list_materials_by_category")
    finally:
        teardown(ctx)


def test_get_material():
    app, ctx, cat, merchant = setup_app()
    try:
        m = material_service.create_material(name="Plywood")
        fetched = material_service.get_material(m.id)
        assert fetched is not None
        assert fetched.name == "Plywood"

        assert material_service.get_material(9999) is None
        print("PASS: test_get_material")
    finally:
        teardown(ctx)


def test_update_material():
    app, ctx, cat, merchant = setup_app()
    try:
        m = material_service.create_material(name="Old Name", default_price=5.00)

        updated = material_service.update_material(
            m.id,
            name="New Name",
            default_price=7.50,
            sku="NEW-SKU",
            brand="BrandX",
            is_active=False,
        )
        assert updated.name == "New Name"
        assert float(updated.default_price) == 7.50
        assert updated.sku == "NEW-SKU"
        assert updated.brand == "BrandX"
        assert updated.is_active is False

        print("PASS: test_update_material")
    finally:
        teardown(ctx)


def test_update_material_validation():
    app, ctx, cat, merchant = setup_app()
    try:
        m = material_service.create_material(name="Test")

        # Empty name
        try:
            material_service.update_material(m.id, name="")
            assert False
        except ValueError:
            pass

        # Negative price
        try:
            material_service.update_material(m.id, default_price=-5)
            assert False
        except ValueError:
            pass

        # Non-existent material
        try:
            material_service.update_material(9999, name="Nope")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_material_validation")
    finally:
        teardown(ctx)


def test_delete_material():
    app, ctx, cat, merchant = setup_app()
    try:
        m = material_service.create_material(name="To Delete")
        mid = m.id

        result = material_service.delete_material(mid)
        assert result is True
        assert material_service.get_material(mid) is None

        # Non-existent
        try:
            material_service.delete_material(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_material")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_material()
    test_create_material_validation()
    test_list_materials()
    test_list_materials_by_category()
    test_get_material()
    test_update_material()
    test_update_material_validation()
    test_delete_material()
    print("\nAll tests passed!")
