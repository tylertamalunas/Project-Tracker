# Page Map — MVP

## Primary Navigation

Top-level navigation for MVP:

* Dashboard
* Projects
* Materials
* Tools

Media is accessed from within projects rather than from a global top-level nav item.

---

## 1. Dashboard / Home

**Purpose**
Provide a simple overview of the application and quick access to active work.

**Route**
`/`

**Contents**

* Summary cards

  * total project count
  * active project count
  * completed project count
  * total actual spend across all projects
* recent or active projects list
* quick links to create a new project

**UI Elements**

* summaries/cards
* small table or list of projects
* navigation links

**Needs**

* summaries
* table/list
* no main form

---

## 2. Project List

**Purpose**
Show all projects and allow filtering by status.

**Route**
`/projects`

**Contents**

* list of all projects
* project name
* status
* created date
* total estimated cost
* total actual cost
* variance
* actions:

  * view
  * edit (if not completed)

**UI Elements**

* table
* filter controls
* action links/buttons

**Needs**

* table
* summary/filter controls
* no main form

---

## 3. Project Detail

**Purpose**
Show a full view of one project and everything associated with it.

**Route**
`/projects/<id>`

**Contents**

* project metadata

  * name
  * description
  * status
  * optional dates
* project summaries

  * estimated total
  * actual total
  * variance
* materials used in the project
* tools used in the project
* media attached to the project
* actions:

  * add material
  * add tool
  * upload media
  * edit project
  * mark completed / reopen

**UI Elements**

* summary section
* materials table
* tools table
* media list/gallery
* action buttons

**Needs**

* summaries
* tables
* media section
* no direct full-page form

---

## 4. Create Project

**Purpose**
Create a new project.

**Route**
`/projects/new`

**Contents**

* form fields:

  * name
  * description
  * status
  * optional start date
  * optional end date

**UI Elements**

* form

**Needs**

* form only

---

## 5. Edit Project

**Purpose**
Edit an existing project.

**Route**
`/projects/<id>/edit`

**Contents**

* same form fields as create project
* status update controls

**Rules**

* unavailable or read-only when project status is `completed`

**UI Elements**

* form

**Needs**

* form only

---

## 6. Material List

**Purpose**
Manage the global material catalog.

**Route**
`/materials`

**Contents**

* list of all materials
* default price
* unit of measure
* category
* merchant
* actions:

  * create
  * edit
  * optionally delete

**UI Elements**

* table
* action buttons

**Needs**

* table
* no main form on list page

---

## 7. Create Material

**Purpose**
Add a new material to the global catalog.

**Route**
`/materials/new`

**Contents**

* form fields:

  * name
  * default price
  * unit of measure
  * category
  * merchant
  * notes

**UI Elements**

* form

**Needs**

* form only

---

## 8. Edit Material

**Purpose**
Edit a global material record.

**Route**
`/materials/<id>/edit`

**Contents**

* same fields as create material

**UI Elements**

* form

**Needs**

* form only

---

## 9. Tool List

**Purpose**
Manage the global tool catalog.

**Route**
`/tools`

**Contents**

* list of all tools
* default price
* category
* actions:

  * create
  * edit
  * optionally delete

**UI Elements**

* table
* action buttons

**Needs**

* table
* no main form on list page

---

## 10. Create Tool

**Purpose**
Add a new tool to the global catalog.

**Route**
`/tools/new`

**Contents**

* form fields:

  * name
  * default price
  * category
  * notes

**UI Elements**

* form

**Needs**

* form only

---

## 11. Edit Tool

**Purpose**
Edit a global tool record.

**Route**
`/tools/<id>/edit`

**Contents**

* same fields as create tool

**UI Elements**

* form

**Needs**

* form only

---

## 12. Add Material to Project

**Purpose**
Attach a material to a specific project.

**Route**
`/projects/<id>/materials/new`

**Contents**

* select existing material
* quantity
* estimated unit price
* actual unit price
* notes

**Rules**

* unavailable when project status is `completed`

**UI Elements**

* form

**Needs**

* form only

---

## 13. Add Tool to Project

**Purpose**
Attach a tool to a specific project.

**Route**
`/projects/<id>/tools/new`

**Contents**

* select existing tool
* quantity
* already owned
* estimated unit price
* actual unit price
* notes

**Rules**

* unavailable when project status is `completed`

**UI Elements**

* form

**Needs**

* form only

---

## 14. Upload Media to Project

**Purpose**
Attach media files to a project.

**Route**
`/projects/<id>/media/new`

**Contents**

* file upload input
* media type
* notes

**Rules**

* unavailable when project status is `completed`

**UI Elements**

* form

**Needs**

* form only

---

## 15. View Project Media

**Purpose**
View media attached to a specific project.

**Route**
`/projects/<id>/media`

**Contents**

* list or gallery of uploaded files
* file name
* media type
* upload date
* actions:

  * view
  * download
  * delete (if project not completed)

**UI Elements**

* table or gallery/list

**Needs**

* table/list
* no main form

---

## Page Type Summary

### Pages with forms

* Create Project
* Edit Project
* Create Material
* Edit Material
* Create Tool
* Edit Tool
* Add Material to Project
* Add Tool to Project
* Upload Media to Project

### Pages with tables/lists

* Dashboard
* Project List
* Project Detail
* Material List
* Tool List
* View Project Media

### Pages with summary sections

* Dashboard
* Project Detail
* Project List