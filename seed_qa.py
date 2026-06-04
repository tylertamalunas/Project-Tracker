"""QA Fixture Data Set

Loads a known-good data set designed to cover main workflows and edge cases
for manual testing. Runs ON TOP of the base seed data (requires seed.py first).

Usage:
    python seed.py --reset   # Load base catalog data
    python seed_qa.py        # Add QA-specific scenarios

Scenarios covered:
    1. Empty project (no materials, tools, or media)
    2. Project exactly on budget (variance = $0)
    3. Project over budget (positive variance)
    4. Project with $0 price materials (free samples)
    5. Project with NULL actual prices (not yet purchased)
    6. Project with many items (10+ materials)
    7. Tool marked owned vs purchased on same project
    8. Media linked to specific line items
    9. Deep hierarchy (grandparent -> parent -> child)
    10. Multiple relationship types between projects
"""
import os
import sys
from datetime import date
from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory, Merchant,
    ProjectMaterial, ProjectTool, Media, MediaLink,
    ProjectHierarchy, ProjectRelationship,
)


def main():
    app = create_app()
    with app.app_context():
        # Check base data exists
        if MaterialCategory.query.count() == 0:
            print("ERROR: Base seed data not found. Run 'python seed.py' first.")
            sys.exit(1)

        if Project.query.filter_by(name="QA: Empty Project").first():
            print("QA fixture data already loaded. Use seed.py --reset to start fresh.")
            return

        print("Loading QA fixture data...")

        # Fetch reference data
        lumber = MaterialCategory.query.filter_by(name="Lumber").first()
        paint_cat = MaterialCategory.query.filter_by(name="Paint & Finishes").first()
        fasteners = MaterialCategory.query.filter_by(name="Fasteners").first()
        power = ToolCategory.query.filter_by(name="Power Tools").first()
        hand = ToolCategory.query.filter_by(name="Hand Tools").first()
        home_depot = Merchant.query.filter_by(name="Home Depot").first()
        lowes = Merchant.query.filter_by(name="Lowe's").first()

        stud = Material.query.filter_by(name="2x4x8 Stud").first()
        plywood = Material.query.filter_by(name='4x8 Plywood (3/4")').first()
        screws = Material.query.filter_by(name="#8 x 2.5\" Wood Screws (100pk)").first()
        paint = Material.query.filter_by(name="Interior Latex Paint (1 gal)").first()
        primer = Material.query.filter_by(name="Primer (1 gal)").first()
        tile = Material.query.filter_by(name="Porcelain Floor Tile (1 sqft)").first()
        pex = Material.query.filter_by(name='1/2" PEX Tubing (10ft)').first()
        nails = Material.query.filter_by(name="16d Framing Nails (5lb)").first()
        romex = Material.query.filter_by(name="12/2 Romex Wire (50ft)").first()
        pine = Material.query.filter_by(name="1x4x8 Pine Board").first()

        drill = Tool.query.filter_by(name="Cordless Drill/Driver").first()
        saw = Tool.query.filter_by(name="Circular Saw").first()
        sander = Tool.query.filter_by(name="Random Orbit Sander").first()
        hammer = Tool.query.filter_by(name="Hammer (16 oz)").first()
        level = Tool.query.filter_by(name="4ft Level").first()
        tape = Tool.query.filter_by(name="25ft Tape Measure").first()
        knife = Tool.query.filter_by(name="Utility Knife").first()

        # ============================================================
        # Scenario 1: Empty project (tests empty state display)
        # ============================================================
        p_empty = Project(
            name="QA: Empty Project",
            description="Project with no materials, tools, or media. Tests empty state UI.",
            status="planned",
            budget_estimate=500.00,
            notes="This project intentionally has nothing attached.",
        )
        db.session.add(p_empty)
        db.session.commit()
        print("  [1] Empty project")

        # ============================================================
        # Scenario 2: Exactly on budget (variance = $0)
        # ============================================================
        p_on_budget = Project(
            name="QA: Exactly On Budget",
            description="Estimated and actual costs match perfectly.",
            status="active",
            start_date=date(2026, 5, 1),
            budget_estimate=100.00,
        )
        db.session.add(p_on_budget)
        db.session.commit()

        # 10 studs at $4.00 each = $40, plus 1 paint at $60 = $100 total
        db.session.add(ProjectMaterial(
            project_id=p_on_budget.id, material_id=stud.id,
            quantity=10, unit_of_measure="each",
            estimated_unit_price=4.00, actual_unit_price=4.00,
            merchant_id=home_depot.id, purchased_on=date(2026, 5, 2)))
        db.session.add(ProjectMaterial(
            project_id=p_on_budget.id, material_id=paint.id,
            quantity=1, unit_of_measure="gallon",
            estimated_unit_price=60.00, actual_unit_price=60.00,
            merchant_id=lowes.id, purchased_on=date(2026, 5, 2)))
        db.session.commit()
        print("  [2] Exactly on budget (variance = $0)")

        # ============================================================
        # Scenario 3: Over budget (tests red variance display)
        # ============================================================
        p_over = Project(
            name="QA: Over Budget",
            description="Actual costs significantly exceed estimates.",
            status="active",
            start_date=date(2026, 4, 1),
            budget_estimate=200.00,
            notes="Price increases hit hard on this one.",
        )
        db.session.add(p_over)
        db.session.commit()

        db.session.add(ProjectMaterial(
            project_id=p_over.id, material_id=plywood.id,
            quantity=4, unit_of_measure="sheet",
            estimated_unit_price=45.00, actual_unit_price=62.00,  # $17/sheet over
            merchant_id=home_depot.id, purchased_on=date(2026, 4, 5),
            notes="Price went up since last checked"))
        db.session.add(ProjectTool(
            project_id=p_over.id, tool_id=saw.id,
            quantity=1, already_owned=False,
            estimated_unit_price=129.00, actual_unit_price=149.00,  # $20 over
            merchant_id=home_depot.id, purchased_on=date(2026, 4, 3)))
        db.session.commit()
        print("  [3] Over budget project")

        # ============================================================
        # Scenario 4: $0 price materials (free samples / donations)
        # ============================================================
        p_free = Project(
            name="QA: Free Materials",
            description="Some materials were donated or free samples.",
            status="active",
            budget_estimate=0,
        )
        db.session.add(p_free)
        db.session.commit()

        db.session.add(ProjectMaterial(
            project_id=p_free.id, material_id=paint.id,
            quantity=1, unit_of_measure="gallon",
            estimated_unit_price=0, actual_unit_price=0,
            notes="Free sample from paint store"))
        db.session.add(ProjectMaterial(
            project_id=p_free.id, material_id=screws.id,
            quantity=2, unit_of_measure="box",
            estimated_unit_price=0, actual_unit_price=0,
            notes="Donated by neighbor"))
        db.session.commit()
        print("  [4] Free/donated materials ($0 prices)")

        # ============================================================
        # Scenario 5: NULL actual prices (not yet purchased)
        # ============================================================
        p_null = Project(
            name="QA: Estimates Only",
            description="All items are estimated but not yet purchased.",
            status="planned",
            budget_estimate=1000.00,
            notes="Shopping list for next month.",
        )
        db.session.add(p_null)
        db.session.commit()

        for mat, qty, price in [(stud, 20, 3.98), (plywood, 4, 45.00),
                                 (screws, 2, 9.97), (nails, 1, 12.50),
                                 (paint, 2, 34.98)]:
            db.session.add(ProjectMaterial(
                project_id=p_null.id, material_id=mat.id,
                quantity=qty, estimated_unit_price=price,
                actual_unit_price=None))  # Not purchased yet
        db.session.commit()
        print("  [5] Estimates only (NULL actuals)")

        # ============================================================
        # Scenario 6: Many items (tests table display with lots of rows)
        # ============================================================
        p_many = Project(
            name="QA: Many Items",
            description="Project with many materials and tools to test scrolling/pagination.",
            status="active",
            start_date=date(2026, 6, 1),
            budget_estimate=5000.00,
        )
        db.session.add(p_many)
        db.session.commit()

        all_materials = Material.query.all()
        for i, mat in enumerate(all_materials):
            db.session.add(ProjectMaterial(
                project_id=p_many.id, material_id=mat.id,
                quantity=(i + 1) * 2, unit_of_measure=mat.unit_of_measure,
                estimated_unit_price=float(mat.default_price),
                actual_unit_price=float(mat.default_price) * 0.9 if i % 2 == 0 else None,
                merchant_id=home_depot.id if i % 2 == 0 else lowes.id))

        all_tools = Tool.query.all()
        for i, tool in enumerate(all_tools):
            db.session.add(ProjectTool(
                project_id=p_many.id, tool_id=tool.id,
                quantity=1, already_owned=(i % 3 == 0),  # Every 3rd tool owned
                estimated_unit_price=float(tool.default_price),
                actual_unit_price=float(tool.default_price) if i % 3 != 0 else 0))
        db.session.commit()
        print("  [6] Many items (10 materials, 12 tools)")

        # ============================================================
        # Scenario 7: Mixed owned/purchased on same project
        # ============================================================
        p_mixed = Project(
            name="QA: Mixed Tool Ownership",
            description="Same project has both owned and purchased tools.",
            status="active",
            budget_estimate=300.00,
        )
        db.session.add(p_mixed)
        db.session.commit()

        db.session.add(ProjectTool(
            project_id=p_mixed.id, tool_id=drill.id,
            quantity=1, already_owned=True,
            estimated_unit_price=0, actual_unit_price=0,
            notes="Had this from a previous project"))
        db.session.add(ProjectTool(
            project_id=p_mixed.id, tool_id=sander.id,
            quantity=1, already_owned=False,
            estimated_unit_price=59.00, actual_unit_price=55.00,
            merchant_id=home_depot.id, purchased_on=date(2026, 5, 15),
            notes="New purchase for this project"))
        db.session.add(ProjectTool(
            project_id=p_mixed.id, tool_id=hammer.id,
            quantity=1, already_owned=True,
            estimated_unit_price=0, actual_unit_price=0))
        db.session.add(ProjectTool(
            project_id=p_mixed.id, tool_id=knife.id,
            quantity=1, already_owned=False,
            estimated_unit_price=8.00, actual_unit_price=7.50,
            merchant_id=lowes.id))
        db.session.commit()
        print("  [7] Mixed tool ownership")

        # ============================================================
        # Scenario 8: Media with line item links
        # ============================================================
        upload_folder = app.config["UPLOAD_FOLDER"]

        def _stub(project_id, filename, content):
            pdir = os.path.join(upload_folder, str(project_id))
            os.makedirs(pdir, exist_ok=True)
            with open(os.path.join(pdir, filename), "w") as f:
                f.write(content)
            return Media(project_id=project_id, file_path=f"{project_id}/{filename}",
                         file_name=filename)

        m1 = _stub(p_over.id, "plywood_receipt.txt", "Receipt: 4 sheets plywood @ $62 = $248")
        m1.media_type = "receipt"
        m1.notes = "Shows the price increase"

        m2 = _stub(p_over.id, "saw_receipt.txt", "Receipt: Circular saw @ $149")
        m2.media_type = "receipt"
        m2.notes = "Tool purchase receipt"

        m3 = _stub(p_many.id, "shopping_list.txt", "Full materials list for the project")
        m3.media_type = "document"
        m3.notes = "Planning document"

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        # Link receipts to specific line items
        plywood_pm = ProjectMaterial.query.filter_by(
            project_id=p_over.id, material_id=plywood.id).first()
        saw_pt = ProjectTool.query.filter_by(
            project_id=p_over.id, tool_id=saw.id).first()

        db.session.add(MediaLink(media_id=m1.id, linked_entity_type="project_material",
                                  linked_entity_id=plywood_pm.id))
        db.session.add(MediaLink(media_id=m2.id, linked_entity_type="project_tool",
                                  linked_entity_id=saw_pt.id))
        db.session.commit()
        print("  [8] Media with line item links")

        # ============================================================
        # Scenario 9: Deep hierarchy (3 levels)
        # ============================================================
        p_grand = Project(name="QA: Grandparent Project", status="active",
                          description="Top level of a 3-deep hierarchy.")
        db.session.add(p_grand)
        db.session.commit()

        p_mid = Project(name="QA: Middle Child", status="active",
                        description="Middle of hierarchy. Has parent and child.")
        db.session.add(p_mid)
        db.session.commit()

        p_leaf = Project(name="QA: Leaf Child", status="planned",
                         description="Bottom of hierarchy. Has parent but no children.")
        db.session.add(p_leaf)
        db.session.commit()

        db.session.add(ProjectHierarchy(parent_project_id=p_grand.id, child_project_id=p_mid.id))
        db.session.add(ProjectHierarchy(parent_project_id=p_mid.id, child_project_id=p_leaf.id))
        db.session.commit()
        print("  [9] Deep hierarchy (3 levels)")

        # ============================================================
        # Scenario 10: Multiple relationship types
        # ============================================================
        db.session.add(ProjectRelationship(
            project_id=p_over.id, related_project_id=p_on_budget.id,
            relationship_type="similar_to", notes="Same materials, different outcomes"))
        db.session.add(ProjectRelationship(
            project_id=p_many.id, related_project_id=p_empty.id,
            relationship_type="follow_up", notes="Empty will use leftover materials"))
        db.session.add(ProjectRelationship(
            project_id=p_null.id, related_project_id=p_over.id,
            relationship_type="depends_on", notes="Waiting for over-budget to finish"))
        db.session.commit()
        print("  [10] Multiple relationship types")

        print(f"\nQA fixture data loaded! Added {Project.query.count()} total projects.")
        print("\nQA Scenarios to test:")
        print(f"  Empty project:      /projects/{p_empty.id}")
        print(f"  On budget:          /projects/{p_on_budget.id}")
        print(f"  Over budget:        /projects/{p_over.id}")
        print(f"  Free materials:     /projects/{p_free.id}")
        print(f"  Estimates only:     /projects/{p_null.id}")
        print(f"  Many items:         /projects/{p_many.id}")
        print(f"  Mixed ownership:    /projects/{p_mixed.id}")
        print(f"  Deep hierarchy:     /projects/{p_grand.id}")


if __name__ == "__main__":
    main()
