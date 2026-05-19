"""Seed script: populates the database with sample categories, merchants, materials, and tools.

Usage:
    python seed.py          # Insert seed data (skips if data already exists)
    python seed.py --reset  # Drop all data and re-seed from scratch
"""
import sys
from app import create_app, db
from app.models import (
    MaterialCategory,
    ToolCategory,
    Merchant,
    Material,
    Tool,
)


def clear_data():
    """Remove all seed-able data (preserves projects and user content)."""
    Material.query.delete()
    Tool.query.delete()
    Merchant.query.delete()
    MaterialCategory.query.delete()
    ToolCategory.query.delete()
    db.session.commit()
    print("Cleared existing catalog data.")


def seed_material_categories():
    categories = [
        {"name": "Lumber", "description": "Wood boards, plywood, trim, and framing materials"},
        {"name": "Fasteners", "description": "Screws, nails, bolts, and anchors"},
        {"name": "Paint & Finishes", "description": "Interior/exterior paint, stains, and sealers"},
        {"name": "Plumbing", "description": "Pipes, fittings, valves, and fixtures"},
        {"name": "Electrical", "description": "Wire, outlets, switches, and breakers"},
        {"name": "Flooring", "description": "Tile, hardwood, laminate, and vinyl"},
        {"name": "Adhesives & Sealants", "description": "Caulk, construction adhesive, and epoxy"},
    ]
    for data in categories:
        db.session.add(MaterialCategory(**data))
    db.session.commit()
    print(f"  Added {len(categories)} material categories.")


def seed_tool_categories():
    categories = [
        {"name": "Power Tools", "description": "Drills, saws, sanders, and routers"},
        {"name": "Hand Tools", "description": "Hammers, screwdrivers, pliers, and wrenches"},
        {"name": "Measuring & Layout", "description": "Tape measures, levels, and squares"},
        {"name": "Safety Equipment", "description": "Goggles, gloves, ear protection, and masks"},
        {"name": "Painting Tools", "description": "Brushes, rollers, trays, and sprayers"},
    ]
    for data in categories:
        db.session.add(ToolCategory(**data))
    db.session.commit()
    print(f"  Added {len(categories)} tool categories.")


def seed_merchants():
    merchants = [
        {"name": "Home Depot", "website": "https://www.homedepot.com", "notes": ""},
        {"name": "Lowe's", "website": "https://www.lowes.com", "notes": ""},
        {"name": "Menards", "website": "https://www.menards.com", "notes": "Midwest locations"},
        {"name": "Ace Hardware", "website": "https://www.acehardware.com", "notes": "Local franchise"},
        {"name": "Amazon", "website": "https://www.amazon.com", "notes": "Online only"},
    ]
    for data in merchants:
        db.session.add(Merchant(**data))
    db.session.commit()
    print(f"  Added {len(merchants)} merchants.")


def seed_materials():
    # Fetch categories and merchants by name for FK references
    lumber = MaterialCategory.query.filter_by(name="Lumber").first()
    fasteners = MaterialCategory.query.filter_by(name="Fasteners").first()
    paint = MaterialCategory.query.filter_by(name="Paint & Finishes").first()
    plumbing = MaterialCategory.query.filter_by(name="Plumbing").first()
    electrical = MaterialCategory.query.filter_by(name="Electrical").first()
    flooring = MaterialCategory.query.filter_by(name="Flooring").first()

    home_depot = Merchant.query.filter_by(name="Home Depot").first()
    lowes = Merchant.query.filter_by(name="Lowe's").first()
    menards = Merchant.query.filter_by(name="Menards").first()

    materials = [
        {"name": "2x4x8 Stud", "default_price": 3.98, "unit_of_measure": "each", "category_id": lumber.id, "merchant_id": home_depot.id},
        {"name": "4x8 Plywood (3/4\")", "default_price": 45.00, "unit_of_measure": "sheet", "category_id": lumber.id, "merchant_id": home_depot.id},
        {"name": "1x4x8 Pine Board", "default_price": 5.48, "unit_of_measure": "each", "category_id": lumber.id, "merchant_id": lowes.id},
        {"name": "#8 x 2.5\" Wood Screws (100pk)", "default_price": 9.97, "unit_of_measure": "box", "category_id": fasteners.id, "merchant_id": home_depot.id},
        {"name": "16d Framing Nails (5lb)", "default_price": 12.50, "unit_of_measure": "box", "category_id": fasteners.id, "merchant_id": menards.id},
        {"name": "Interior Latex Paint (1 gal)", "default_price": 34.98, "unit_of_measure": "gallon", "category_id": paint.id, "merchant_id": lowes.id},
        {"name": "Primer (1 gal)", "default_price": 22.00, "unit_of_measure": "gallon", "category_id": paint.id, "merchant_id": home_depot.id},
        {"name": "1/2\" PEX Tubing (10ft)", "default_price": 8.50, "unit_of_measure": "length", "category_id": plumbing.id, "merchant_id": home_depot.id},
        {"name": "12/2 Romex Wire (50ft)", "default_price": 42.00, "unit_of_measure": "roll", "category_id": electrical.id, "merchant_id": lowes.id},
        {"name": "Porcelain Floor Tile (1 sqft)", "default_price": 2.49, "unit_of_measure": "sqft", "category_id": flooring.id, "merchant_id": menards.id},
    ]
    for data in materials:
        db.session.add(Material(**data))
    db.session.commit()
    print(f"  Added {len(materials)} materials.")


def seed_tools():
    power = ToolCategory.query.filter_by(name="Power Tools").first()
    hand = ToolCategory.query.filter_by(name="Hand Tools").first()
    measuring = ToolCategory.query.filter_by(name="Measuring & Layout").first()
    safety = ToolCategory.query.filter_by(name="Safety Equipment").first()
    painting = ToolCategory.query.filter_by(name="Painting Tools").first()

    tools = [
        {"name": "Cordless Drill/Driver", "default_price": 99.00, "category_id": power.id},
        {"name": "Circular Saw", "default_price": 129.00, "category_id": power.id},
        {"name": "Random Orbit Sander", "default_price": 59.00, "category_id": power.id},
        {"name": "Hammer (16 oz)", "default_price": 15.00, "category_id": hand.id},
        {"name": "Pry Bar", "default_price": 12.00, "category_id": hand.id},
        {"name": "Utility Knife", "default_price": 8.00, "category_id": hand.id},
        {"name": "25ft Tape Measure", "default_price": 12.00, "category_id": measuring.id},
        {"name": "4ft Level", "default_price": 25.00, "category_id": measuring.id},
        {"name": "Speed Square", "default_price": 10.00, "category_id": measuring.id},
        {"name": "Safety Glasses", "default_price": 8.00, "category_id": safety.id},
        {"name": "Paint Roller Kit", "default_price": 18.00, "category_id": painting.id},
        {"name": "2\" Angled Brush", "default_price": 9.00, "category_id": painting.id},
    ]
    for data in tools:
        db.session.add(Tool(**data))
    db.session.commit()
    print(f"  Added {len(tools)} tools.")


def main():
    app = create_app()
    with app.app_context():
        reset = "--reset" in sys.argv

        if reset:
            clear_data()

        # Check if data already exists
        if MaterialCategory.query.count() > 0 and not reset:
            print("Seed data already exists. Use --reset to clear and re-seed.")
            return

        print("Seeding database...")
        seed_material_categories()
        seed_tool_categories()
        seed_merchants()
        seed_materials()
        seed_tools()
        print("Done! Seed data loaded successfully.")


if __name__ == "__main__":
    main()
