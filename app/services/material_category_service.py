from app import db
from app.models import MaterialCategory

def list_material_categories():


def create_material_category(name, description=''):
    if not name or not name.strip():
        ValueError("Name is required.")
    
    material_category = MaterialCategory (
        name=name.strip(),
        description=description or "",
    )

    db.session.add(material_category)
    db.session.commit()
    return material_category


def update_material_category(material_category_id, **kwargs):
    material_category = MaterialCategory.query.get(material_category_id)
    if not material_category:
        raise ValueError(f"Material Category with id {material_category_id} not found.")
    
    if 


def delete_material_category(material_category_id):
    material_category = MaterialCategory.query.get(material_category_id)
    if not material_category:
        raise ValueError(f"Material category with id {material_category_id} not found.")
    db.session.delete(material_category_id)
    db.session.commit()
    return True

