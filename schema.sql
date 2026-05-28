-- Project Tracker - SQLite Schema
-- Generated from approved Mermaid ER diagram + domain decisions
-- Foreign keys must be enabled per connection: PRAGMA foreign_keys = ON;

-- ============================================================
-- Core Tables
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'completed')),
    start_date TEXT,          -- ISO 8601 date, optional/informational
    end_date TEXT,            -- ISO 8601 date, optional/informational
    budget_estimate REAL CHECK (budget_estimate IS NULL OR budget_estimate >= 0),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Lookup / Category Tables
-- ============================================================

CREATE TABLE IF NOT EXISTS material_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tool_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    website TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Global Catalogs
-- ============================================================

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    default_price REAL DEFAULT 0 CHECK (default_price >= 0),
    unit_of_measure TEXT DEFAULT '',
    sku TEXT DEFAULT '',
    brand TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    category_id INTEGER,
    merchant_id INTEGER,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES material_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    default_price REAL DEFAULT 0 CHECK (default_price >= 0),
    brand TEXT DEFAULT '',
    model_number TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    category_id INTEGER,
    merchant_id INTEGER,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES tool_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE SET NULL
);

-- ============================================================
-- Project Junction Tables
-- ============================================================

CREATE TABLE IF NOT EXISTS project_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    merchant_id INTEGER,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_of_measure TEXT DEFAULT '',
    estimated_unit_price REAL NOT NULL DEFAULT 0 CHECK (estimated_unit_price >= 0),
    actual_unit_price REAL CHECK (actual_unit_price IS NULL OR actual_unit_price >= 0),
    notes TEXT DEFAULT '',
    purchased_on TEXT DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE RESTRICT,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS project_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    merchant_id INTEGER,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    already_owned INTEGER NOT NULL DEFAULT 0 CHECK (already_owned IN (0, 1)),
    estimated_unit_price REAL NOT NULL DEFAULT 0 CHECK (estimated_unit_price >= 0),
    actual_unit_price REAL CHECK (actual_unit_price IS NULL OR actual_unit_price >= 0),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE RESTRICT,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE SET NULL
);

-- ============================================================
-- Media
-- ============================================================

CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    media_type TEXT DEFAULT 'other' CHECK (media_type IN ('receipt', 'progress', 'document', 'other')),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS media_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER NOT NULL,
    linked_entity_type TEXT NOT NULL,
    linked_entity_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE
);

-- ============================================================
-- Future / Reserved Tables
-- ============================================================

CREATE TABLE IF NOT EXISTS project_hierarchy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_project_id INTEGER NOT NULL,
    child_project_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (parent_project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (child_project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    related_project_id INTEGER NOT NULL,
    relationship_type TEXT DEFAULT 'related',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (related_project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES
-- ============================================================

-- projects.status: filter project list by status (planned/active/completed)
CREATE INDEX IF NOT EXISTS ix_projects_status ON projects(status);

-- projects.created_at: sort project list by creation date
CREATE INDEX IF NOT EXISTS ix_projects_created_at ON projects(created_at);

-- materials.category_id: join materials to their category for catalog views
CREATE INDEX IF NOT EXISTS ix_materials_category_id ON materials(category_id);

-- materials.merchant_id: join materials to merchant for catalog views
CREATE INDEX IF NOT EXISTS ix_materials_merchant_id ON materials(merchant_id);

-- tools.category_id: join tools to their category for catalog views
CREATE INDEX IF NOT EXISTS ix_tools_category_id ON tools(category_id);

-- tools.merchant_id: join tools to their merchant for catalog views
CREATE INDEX IF NOT EXISTS ix_tools_merchant_id ON tools(merchant_id);

-- project_materials.project_id: load all materials for a given project
CREATE INDEX IF NOT EXISTS ix_project_materials_project_id ON project_materials(project_id);

-- project_materials.material_id: find which projects use a specific material
CREATE INDEX IF NOT EXISTS ix_project_materials_material_id ON project_materials(material_id);

-- project_tools.project_id: load all tools for a given project
CREATE INDEX IF NOT EXISTS ix_project_tools_project_id ON project_tools(project_id);

-- project_tools.tool_id: find which projects use a specific tool
CREATE INDEX IF NOT EXISTS ix_project_tools_tool_id ON project_tools(tool_id);

-- media.project_id: load all media for a given project
CREATE INDEX IF NOT EXISTS ix_media_project_id ON media(project_id);

-- media_links.media_id: find all links for a media record
CREATE INDEX IF NOT EXISTS ix_media_links_media_id ON media_links(media_id);

-- project_hierarchy FKs (future)
CREATE INDEX IF NOT EXISTS ix_project_hierarchy_parent ON project_hierarchy(parent_project_id);
CREATE INDEX IF NOT EXISTS ix_project_hierarchy_child ON project_hierarchy(child_project_id);

-- project_relationships FKs (future)
CREATE INDEX IF NOT EXISTS ix_project_relationships_project ON project_relationships(project_id);
CREATE INDEX IF NOT EXISTS ix_project_relationships_related ON project_relationships(related_project_id);
