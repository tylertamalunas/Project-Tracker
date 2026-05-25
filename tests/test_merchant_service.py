"""Tests for the merchant service layer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.services import merchant_service


def setup_app():
    """Create app with in-memory DB."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_merchant():
    app, ctx = setup_app()
    try:
        m = merchant_service.create_merchant(
            name="Home Depot",
            website="https://www.homedepot.com",
            notes="Main supplier",
        )
        assert m.id is not None
        assert m.name == "Home Depot"
        assert m.website == "https://www.homedepot.com"
        assert m.notes == "Main supplier"
        assert m.created_at is not None
        print("PASS: test_create_merchant")
    finally:
        teardown(ctx)


def test_create_merchant_validation():
    app, ctx = setup_app()
    try:
        # Empty name
        try:
            merchant_service.create_merchant(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "required" in str(e).lower()

        # Whitespace-only name
        try:
            merchant_service.create_merchant(name="   ")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "required" in str(e).lower()

        print("PASS: test_create_merchant_validation")
    finally:
        teardown(ctx)


def test_list_merchants():
    app, ctx = setup_app()
    try:
        merchant_service.create_merchant(name="Ace Hardware")
        merchant_service.create_merchant(name="Home Depot")
        merchant_service.create_merchant(name="Lowe's")

        # All
        all_merchants = merchant_service.list_merchants()
        assert len(all_merchants) == 3
        # Should be ordered by name
        assert all_merchants[0].name == "Ace Hardware"

        # Filter by partial name
        filtered = merchant_service.list_merchants(name_filter="home")
        assert len(filtered) == 1
        assert filtered[0].name == "Home Depot"

        # No match
        empty = merchant_service.list_merchants(name_filter="xyz")
        assert len(empty) == 0

        print("PASS: test_list_merchants")
    finally:
        teardown(ctx)


def test_get_merchant():
    app, ctx = setup_app()
    try:
        m = merchant_service.create_merchant(name="Menards")
        fetched = merchant_service.get_merchant(m.id)
        assert fetched is not None
        assert fetched.name == "Menards"

        assert merchant_service.get_merchant(9999) is None
        print("PASS: test_get_merchant")
    finally:
        teardown(ctx)


def test_update_merchant():
    app, ctx = setup_app()
    try:
        m = merchant_service.create_merchant(name="Old Name", website="http://old.com")

        updated = merchant_service.update_merchant(
            m.id,
            name="New Name",
            website="https://new.com",
            notes="Updated notes",
        )
        assert updated.name == "New Name"
        assert updated.website == "https://new.com"
        assert updated.notes == "Updated notes"

        print("PASS: test_update_merchant")
    finally:
        teardown(ctx)


def test_update_merchant_validation():
    app, ctx = setup_app()
    try:
        m = merchant_service.create_merchant(name="Test")

        # Empty name
        try:
            merchant_service.update_merchant(m.id, name="")
            assert False
        except ValueError:
            pass

        # Non-existent merchant
        try:
            merchant_service.update_merchant(9999, name="Nope")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_merchant_validation")
    finally:
        teardown(ctx)


def test_delete_merchant():
    app, ctx = setup_app()
    try:
        m = merchant_service.create_merchant(name="To Delete")
        mid = m.id

        result = merchant_service.delete_merchant(mid)
        assert result is True
        assert merchant_service.get_merchant(mid) is None

        # Non-existent
        try:
            merchant_service.delete_merchant(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_merchant")
    finally:
        teardown(ctx)


def test_merchant_with_purchase_records():
    """Verify merchant can be referenced from project purchase records."""
    app, ctx = setup_app()
    try:
        from app.models import Project, Material, MaterialCategory, ProjectMaterial

        m = merchant_service.create_merchant(name="Amazon")
        cat = MaterialCategory(name="Lumber")
        db.session.add(cat)
        db.session.commit()

        mat = Material(name="2x4", default_price=4.00, category_id=cat.id, merchant_id=m.id)
        db.session.add(mat)
        db.session.commit()

        proj = Project(name="Test Project", status="active")
        db.session.add(proj)
        db.session.commit()

        pm = ProjectMaterial(
            project_id=proj.id,
            material_id=mat.id,
            merchant_id=m.id,
            quantity=10,
            estimated_unit_price=4.00,
        )
        db.session.add(pm)
        db.session.commit()

        # Verify relationships
        assert pm.merchant.name == "Amazon"
        assert mat.merchant.name == "Amazon"
        assert len(m.project_materials) == 1
        assert len(m.materials) == 1

        print("PASS: test_merchant_with_purchase_records")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_merchant()
    test_create_merchant_validation()
    test_list_merchants()
    test_get_merchant()
    test_update_merchant()
    test_update_merchant_validation()
    test_delete_merchant()
    test_merchant_with_purchase_records()
    print("\nAll tests passed!")
