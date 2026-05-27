"""Tests for the material category service layer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Material
from app.services import material_category_service


def setup_app():
    """Create app with in-memory DB."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_category():
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(
            name="Lumber",
            description="Wood boards and framing materials",
        )
        assert cat.id is not None
        assert cat.name == "Lumber"
        assert cat.description == "Wood boards and framing materials"
        assert cat.created_at is not None
        print("PASS: test_create_category")
    finally:
        teardown(ctx)


def test_create_category_validation():
    app, ctx = setup_app()
    try:
        # Empty name
        try:
            material_category_service.create_material_category(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "required" in str(e).lower()

        # Duplicate name
        material_category_service.create_material_category(name="Fasteners")
        try:
            material_category_service.create_material_category(name="Fasteners")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Duplicate name (case-insensitive)
        try:
            material_category_service.create_material_category(name="fasteners")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already exists" in str(e).lower()

        print("PASS: test_create_category_validation")
    finally:
        teardown(ctx)


def test_list_categories():
    app, ctx = setup_app()
    try:
        material_category_service.create_material_category(name="Plumbing")
        material_category_service.create_material_category(name="Electrical")
        material_category_service.create_material_category(name="Adhesives")

        categories = material_category_service.list_material_categories()
        assert len(categories) == 3
        # Ordered by name
        assert categories[0].name == "Adhesives"
        assert categories[1].name == "Electrical"
        assert categories[2].name == "Plumbing"

        print("PASS: test_list_categories")
    finally:
        teardown(ctx)


def test_get_category():
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(name="Paint")
        fetched = material_category_service.get_material_category(cat.id)
        assert fetched is not None
        assert fetched.name == "Paint"

        assert material_category_service.get_material_category(9999) is None
        print("PASS: test_get_category")
    finally:
        teardown(ctx)


def test_update_category():
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(name="Old Name")

        updated = material_category_service.update_material_category(
            cat.id,
            name="New Name",
            description="Updated description",
        )
        assert updated.name == "New Name"
        assert updated.description == "Updated description"

        print("PASS: test_update_category")
    finally:
        teardown(ctx)


def test_update_category_validation():
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(name="Flooring")
        material_category_service.create_material_category(name="Lumber")

        # Empty name
        try:
            material_category_service.update_material_category(cat.id, name="")
            assert False
        except ValueError:
            pass

        # Duplicate name
        try:
            material_category_service.update_material_category(cat.id, name="Lumber")
            assert False
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Non-existent category
        try:
            material_category_service.update_material_category(9999, name="Nope")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_category_validation")
    finally:
        teardown(ctx)


def test_delete_category():
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(name="To Delete")
        cid = cat.id

        result = material_category_service.delete_material_category(cid)
        assert result is True
        assert material_category_service.get_material_category(cid) is None

        # Non-existent
        try:
            material_category_service.delete_material_category(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_category")
    finally:
        teardown(ctx)


def test_delete_nullifies_material_reference():
    """Verify deleting a category sets material.category_id to NULL."""
    app, ctx = setup_app()
    try:
        cat = material_category_service.create_material_category(name="Temp Category")
        mat = Material(name="Test Material", default_price=5.00, category_id=cat.id)
        db.session.add(mat)
        db.session.commit()

        assert mat.category_id == cat.id

        material_category_service.delete_material_category(cat.id)
        db.session.refresh(mat)
        assert mat.category_id is None

        print("PASS: test_delete_nullifies_material_reference")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_category()
    test_create_category_validation()
    test_list_categories()
    test_get_category()
    test_update_category()
    test_update_category_validation()
    test_delete_category()
    test_delete_nullifies_material_reference()
    print("\nAll tests passed!")
