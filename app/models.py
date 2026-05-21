from datetime import datetime, timezone
from app import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), nullable=False, default="planned", index=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    budget_estimate = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project_materials = db.relationship("ProjectMaterial", back_populates="project", cascade="all, delete-orphan")
    project_tools = db.relationship("ProjectTool", back_populates="project", cascade="all, delete-orphan")
    media = db.relationship("Media", back_populates="project", cascade="all, delete-orphan")

    @property
    def estimated_total(self):
        """Sum of (quantity * estimated_unit_price) for materials and tools."""
        material_est = sum(
            pm.quantity * (pm.estimated_unit_price or 0)
            for pm in self.project_materials
        )
        tool_est = sum(
            pt.quantity * (pt.estimated_unit_price or 0)
            for pt in self.project_tools
            if not pt.already_owned
        )
        return material_est + tool_est

    @property
    def actual_total(self):
        """Sum of (quantity * actual_unit_price) for materials and purchased tools."""
        material_act = sum(
            pm.quantity * (pm.actual_unit_price or 0)
            for pm in self.project_materials
        )
        tool_act = sum(
            pt.quantity * (pt.actual_unit_price or 0)
            for pt in self.project_tools
            if not pt.already_owned
        )
        return material_act + tool_act

    @property
    def variance(self):
        """Actual minus estimated. Positive means over budget."""
        return self.actual_total - self.estimated_total


class MaterialCategory(db.Model):
    __tablename__ = "material_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    materials = db.relationship("Material", back_populates="category")


class ToolCategory(db.Model):
    __tablename__ = "tool_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tools = db.relationship("Tool", back_populates="category")


class Merchant(db.Model):
    __tablename__ = "merchants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    website = db.Column(db.String(500), default="")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    materials = db.relationship("Material", back_populates="merchant")


class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    default_price = db.Column(db.Numeric(10, 2), default=0)
    unit_of_measure = db.Column(db.String(50), default="")
    sku = db.Column(db.String(100), default="")
    brand = db.Column(db.String(200), default="")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey("material_categories.id"), nullable=True, index=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey("merchants.id"), nullable=True, index=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = db.relationship("MaterialCategory", back_populates="materials")
    merchant = db.relationship("Merchant", back_populates="materials")
    project_materials = db.relationship("ProjectMaterial", back_populates="material")


class Tool(db.Model):
    __tablename__ = "tools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    default_price = db.Column(db.Numeric(10, 2), default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("tool_categories.id"), nullable=True, index=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = db.relationship("ToolCategory", back_populates="tools")
    project_tools = db.relationship("ProjectTool", back_populates="tool")


class ProjectMaterial(db.Model):
    __tablename__ = "project_materials"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    estimated_unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    actual_unit_price = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship("Project", back_populates="project_materials")
    material = db.relationship("Material", back_populates="project_materials")


class ProjectTool(db.Model):
    __tablename__ = "project_tools"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    already_owned = db.Column(db.Boolean, nullable=False, default=False)
    estimated_unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    actual_unit_price = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship("Project", back_populates="project_tools")
    tool = db.relationship("Tool", back_populates="project_tools")


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    media_type = db.Column(db.String(50), default="other")  # receipt, progress, document, other
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship("Project", back_populates="media")


class MediaLink(db.Model):
    """Links media to entities beyond projects (future use)."""
    __tablename__ = "media_links"

    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False, index=True)
    linked_entity_type = db.Column(db.String(50), nullable=False)
    linked_entity_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    media = db.relationship("Media", backref="links")


class ProjectHierarchy(db.Model):
    """Sub-project relationships (reserved for future use)."""
    __tablename__ = "project_hierarchy"

    id = db.Column(db.Integer, primary_key=True)
    parent_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    child_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ProjectRelationship(db.Model):
    """Linked/related projects (reserved for future use)."""
    __tablename__ = "project_relationships"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    related_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    relationship_type = db.Column(db.String(50), default="related")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
