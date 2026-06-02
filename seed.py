"""Seed script: populates the database with sample categories, merchants, materials, tools, and projects.

Usage:
    python seed.py          # Insert seed data (skips if data already exists)
    python seed.py --reset  # Drop all data and re-seed from scratch
"""
import os
import sys
from datetime import date
from app import create_app, db
from app.models import (
    MaterialCategory,
    ToolCategory,
    Merchant,
    Material,
    Tool,
    Project,
    ProjectMaterial,
    ProjectTool,
    Media,
    MediaLink,
    ProjectHierarchy,
    ProjectRelationship,
)


def clear_data():
    """Remove all seed-able data (preserves nothing on full reset)."""
    MediaLink.query.delete()
    Media.query.delete()
    ProjectHierarchy.query.delete()
    ProjectRelationship.query.delete()
    ProjectMaterial.query.delete()
    ProjectTool.query.delete()
    Project.query.delete()
    Material.query.delete()
    Tool.query.delete()
    Merchant.query.delete()
    MaterialCategory.query.delete()
    ToolCategory.query.delete()
    db.session.commit()
    print("Cleared existing data.")


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


def seed_projects():
    """Create sample projects with materials, tools, hierarchy, relationships, and media."""
    from flask import current_app

    home_depot = Merchant.query.filter_by(name="Home Depot").first()
    lowes = Merchant.query.filter_by(name="Lowe's").first()
    menards = Merchant.query.filter_by(name="Menards").first()

    stud = Material.query.filter_by(name="2x4x8 Stud").first()
    plywood = Material.query.filter_by(name='4x8 Plywood (3/4")').first()
    screws = Material.query.filter_by(name="#8 x 2.5\" Wood Screws (100pk)").first()
    paint = Material.query.filter_by(name="Interior Latex Paint (1 gal)").first()
    primer = Material.query.filter_by(name="Primer (1 gal)").first()
    tile = Material.query.filter_by(name="Porcelain Floor Tile (1 sqft)").first()

    drill = Tool.query.filter_by(name="Cordless Drill/Driver").first()
    saw = Tool.query.filter_by(name="Circular Saw").first()
    tape = Tool.query.filter_by(name="25ft Tape Measure").first()
    roller = Tool.query.filter_by(name="Paint Roller Kit").first()
    sander = Tool.query.filter_by(name="Random Orbit Sander").first()
    level = Tool.query.filter_by(name="4ft Level").first()

    # === Project 1: Parent project (House Renovation - active) ===
    p_parent = Project(
        name="Full House Renovation",
        description="Complete renovation of the main floor including kitchen, bathroom, and living room.",
        status="active",
        start_date=date(2026, 3, 1),
        budget_estimate=15000.00,
        notes="Phase 1: Kitchen & Bathroom. Phase 2: Living Room & Flooring.",
    )
    db.session.add(p_parent)
    db.session.commit()

    # === Project 2: Kitchen Remodel (active, child of House Renovation) ===
    p_kitchen = Project(
        name="Kitchen Cabinet Refresh",
        description="Sand, prime, and repaint all kitchen cabinets. Replace hardware.",
        status="active",
        start_date=date(2026, 4, 15),
        budget_estimate=800.00,
        notes="Using semi-gloss for durability. Color: Swiss Coffee.",
    )
    db.session.add(p_kitchen)
    db.session.commit()

    pm_kitchen = [
        ProjectMaterial(project_id=p_kitchen.id, material_id=paint.id, merchant_id=lowes.id,
                        quantity=3, unit_of_measure="gallon",
                        estimated_unit_price=34.98, actual_unit_price=32.00,
                        purchased_on=date(2026, 4, 16), notes="Color: Swiss Coffee"),
        ProjectMaterial(project_id=p_kitchen.id, material_id=primer.id, merchant_id=home_depot.id,
                        quantity=2, unit_of_measure="gallon",
                        estimated_unit_price=22.00, actual_unit_price=22.00,
                        purchased_on=date(2026, 4, 16)),
        ProjectMaterial(project_id=p_kitchen.id, material_id=screws.id, merchant_id=home_depot.id,
                        quantity=1, unit_of_measure="box",
                        estimated_unit_price=9.97, actual_unit_price=9.97,
                        purchased_on=date(2026, 4, 16)),
    ]
    db.session.add_all(pm_kitchen)

    pt_kitchen = [
        ProjectTool(project_id=p_kitchen.id, tool_id=roller.id, merchant_id=home_depot.id,
                    quantity=1, already_owned=False,
                    estimated_unit_price=18.00, actual_unit_price=18.00,
                    purchased_on=date(2026, 4, 15)),
        ProjectTool(project_id=p_kitchen.id, tool_id=sander.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0, actual_unit_price=0,
                    notes="Already had from deck project"),
        ProjectTool(project_id=p_kitchen.id, tool_id=drill.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0, actual_unit_price=0),
    ]
    db.session.add_all(pt_kitchen)
    db.session.commit()

    # === Project 3: Bathroom Remodel (active, child of House Renovation) ===
    p_bathroom = Project(
        name="Bathroom Tile & Paint",
        description="Retile the shower area and repaint all bathroom walls.",
        status="active",
        start_date=date(2026, 5, 1),
        budget_estimate=1200.00,
        notes="Using waterproof tile adhesive for shower.",
    )
    db.session.add(p_bathroom)
    db.session.commit()

    pm_bathroom = [
        ProjectMaterial(project_id=p_bathroom.id, material_id=tile.id, merchant_id=menards.id,
                        quantity=60, unit_of_measure="sqft",
                        estimated_unit_price=2.49, actual_unit_price=2.29,
                        purchased_on=date(2026, 5, 2), notes="On sale at Menards"),
        ProjectMaterial(project_id=p_bathroom.id, material_id=paint.id, merchant_id=lowes.id,
                        quantity=2, unit_of_measure="gallon",
                        estimated_unit_price=34.98, actual_unit_price=None,
                        notes="Haven't purchased yet"),
        ProjectMaterial(project_id=p_bathroom.id, material_id=primer.id, merchant_id=lowes.id,
                        quantity=1, unit_of_measure="gallon",
                        estimated_unit_price=22.00),
    ]
    db.session.add_all(pm_bathroom)

    pt_bathroom = [
        ProjectTool(project_id=p_bathroom.id, tool_id=level.id,
                    quantity=1, already_owned=False,
                    estimated_unit_price=25.00, actual_unit_price=22.00,
                    merchant_id=home_depot.id, purchased_on=date(2026, 5, 1)),
        ProjectTool(project_id=p_bathroom.id, tool_id=tape.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0, actual_unit_price=0),
    ]
    db.session.add_all(pt_bathroom)
    db.session.commit()

    # === Project 4: Deck Build (planned) ===
    p_deck = Project(
        name="Backyard Deck Build",
        description="12x16 pressure-treated deck with stairs and railing.",
        status="planned",
        budget_estimate=3500.00,
        notes="Waiting on permit approval. Plan to start in July.",
    )
    db.session.add(p_deck)
    db.session.commit()

    pm_deck = [
        ProjectMaterial(project_id=p_deck.id, material_id=stud.id,
                        quantity=48, unit_of_measure="each",
                        estimated_unit_price=3.98),
        ProjectMaterial(project_id=p_deck.id, material_id=plywood.id,
                        quantity=6, unit_of_measure="sheet",
                        estimated_unit_price=45.00),
        ProjectMaterial(project_id=p_deck.id, material_id=screws.id,
                        quantity=3, unit_of_measure="box",
                        estimated_unit_price=9.97),
    ]
    db.session.add_all(pm_deck)

    pt_deck = [
        ProjectTool(project_id=p_deck.id, tool_id=saw.id,
                    quantity=1, already_owned=False,
                    estimated_unit_price=129.00),
        ProjectTool(project_id=p_deck.id, tool_id=drill.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0),
        ProjectTool(project_id=p_deck.id, tool_id=tape.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0),
    ]
    db.session.add_all(pt_deck)
    db.session.commit()

    # === Project 5: Completed project (Hallway Repaint) ===
    p_hallway = Project(
        name="Hallway Repaint",
        description="Repainted the main hallway and stairwell.",
        status="completed",
        start_date=date(2026, 2, 10),
        end_date=date(2026, 2, 14),
        budget_estimate=150.00,
        notes="Came in under budget!",
    )
    db.session.add(p_hallway)
    db.session.commit()

    pm_hallway = [
        ProjectMaterial(project_id=p_hallway.id, material_id=paint.id, merchant_id=home_depot.id,
                        quantity=1, unit_of_measure="gallon",
                        estimated_unit_price=34.98, actual_unit_price=34.98,
                        purchased_on=date(2026, 2, 10)),
        ProjectMaterial(project_id=p_hallway.id, material_id=primer.id, merchant_id=home_depot.id,
                        quantity=1, unit_of_measure="gallon",
                        estimated_unit_price=22.00, actual_unit_price=22.00,
                        purchased_on=date(2026, 2, 10)),
    ]
    db.session.add_all(pm_hallway)

    pt_hallway = [
        ProjectTool(project_id=p_hallway.id, tool_id=roller.id,
                    quantity=1, already_owned=True,
                    estimated_unit_price=0, actual_unit_price=0),
    ]
    db.session.add_all(pt_hallway)
    db.session.commit()

    # === Hierarchy: House Renovation -> Kitchen, Bathroom ===
    db.session.add(ProjectHierarchy(parent_project_id=p_parent.id, child_project_id=p_kitchen.id))
    db.session.add(ProjectHierarchy(parent_project_id=p_parent.id, child_project_id=p_bathroom.id))
    db.session.commit()

    # === Relationships ===
    db.session.add(ProjectRelationship(
        project_id=p_kitchen.id, related_project_id=p_bathroom.id,
        relationship_type="similar_to", notes="Both involve painting"))
    db.session.add(ProjectRelationship(
        project_id=p_deck.id, related_project_id=p_parent.id,
        relationship_type="follow_up", notes="Deck after interior is done"))
    db.session.add(ProjectRelationship(
        project_id=p_bathroom.id, related_project_id=p_hallway.id,
        relationship_type="related", notes="Same paint color scheme"))
    db.session.commit()

    # === Media (placeholder files) ===
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    def _create_placeholder(project_id, filename, content="Placeholder file for testing."):
        """Create a placeholder file on disk and return a Media record."""
        project_dir = os.path.join(upload_folder, str(project_id))
        os.makedirs(project_dir, exist_ok=True)
        file_path = os.path.join(project_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        return Media(
            project_id=project_id,
            file_path=f"{project_id}/{filename}",
            file_name=filename,
        )

    # Kitchen media
    m1 = _create_placeholder(p_kitchen.id, "paint_receipt.txt", "Receipt: 3 gallons Swiss Coffee paint - $96.00")
    m1.media_type = "receipt"
    m1.notes = "Lowe's paint purchase receipt"

    m2 = _create_placeholder(p_kitchen.id, "before_cabinets.txt", "Photo placeholder: kitchen cabinets before sanding")
    m2.media_type = "progress"
    m2.notes = "Before photo - cabinets as found"

    m3 = _create_placeholder(p_kitchen.id, "after_cabinets.txt", "Photo placeholder: kitchen cabinets after painting")
    m3.media_type = "progress"
    m3.notes = "After photo - first coat done"

    # Bathroom media
    m4 = _create_placeholder(p_bathroom.id, "tile_receipt.txt", "Receipt: 60 sqft porcelain tile - $137.40")
    m4.media_type = "receipt"
    m4.notes = "Menards tile purchase"

    m5 = _create_placeholder(p_bathroom.id, "shower_measurement.txt", "Measurement notes: shower 5x3 ft, wall height 8ft")
    m5.media_type = "document"
    m5.notes = "Shower dimensions for tile calculation"

    # Deck media
    m6 = _create_placeholder(p_deck.id, "deck_plan.txt", "Deck plan: 12x16 with stairs on south side")
    m6.media_type = "document"
    m6.notes = "Design sketch and dimensions"

    db.session.add_all([m1, m2, m3, m4, m5, m6])
    db.session.commit()

    # === Media Links (associate receipts with specific line items) ===
    # Link paint receipt to the paint line item on kitchen project
    paint_pm = ProjectMaterial.query.filter_by(project_id=p_kitchen.id, material_id=paint.id).first()
    db.session.add(MediaLink(media_id=m1.id, linked_entity_type="project_material", linked_entity_id=paint_pm.id))

    # Link tile receipt to the tile line item on bathroom project
    tile_pm = ProjectMaterial.query.filter_by(project_id=p_bathroom.id, material_id=tile.id).first()
    db.session.add(MediaLink(media_id=m4.id, linked_entity_type="project_material", linked_entity_id=tile_pm.id))

    # Link roller purchase to roller tool on kitchen
    roller_pt = ProjectTool.query.filter_by(project_id=p_kitchen.id, tool_id=roller.id).first()
    db.session.add(MediaLink(media_id=m1.id, linked_entity_type="project_tool", linked_entity_id=roller_pt.id))

    db.session.commit()

    print(f"  Added 5 projects (with hierarchy, relationships, media, and media links).")


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
        seed_projects()
        print("Done! Seed data loaded successfully.")


if __name__ == "__main__":
    main()
