\# MVP Scope - Project Tracking App



\## Purpose



Define the exact scope of the first usable release (MVP).

This document establishes what will be built and what is explicitly excluded.



\---



\## Core Objective



Build a local web application that allows a single user to:



\* Create and manage projects

\* Track materials and tools used per project

\* Compare estimated vs actual costs

\* Attach and view media (receipts, images, documents)



\---



\## Functional Scope (In Scope)



\### 1. Project Management



\* Create, update, delete, and view projects

\* Each project contains:



&#x20; \* `id`

&#x20; \* `name`

&#x20; \* `description`

&#x20; \* `created\_at`

\* Projects can be marked as \*\*completed\*\*



\---



\### 2. Materials Tracking



\* Materials exist globally and can be reused across projects

\* A project can have multiple materials via a join table



Each `ProjectMaterial` must store:



\* `project\_id`

\* `material\_id`

\* `quantity` (integer > 0)

\* `recorded\_price` (float ≥ 0, fixed at time of entry)



Material total is calculated as:



```

quantity \* recorded\_price

```



\---



\### 3. Tools Tracking



\* Tools exist globally and can be reused across projects

\* A project can have multiple tools via a join table



Each `ProjectTool` must store:



\* `project\_id`

\* `tool\_id`

\* `quantity` (integer > 0)

\* `unit\_price\_at\_time` (float ≥ 0)

\* `already\_owned` (boolean)



Rules:



\* If `already\_owned = true`, cost contribution = 0

\* If `already\_owned = false`, cost = quantity \* unit\_price\_at\_time



\---



\### 4. Cost Tracking (Core Logic)



All costs are \*\*calculated dynamically\*\* (not stored as totals).



Definitions:



\* Project total:



```

sum(ProjectMaterial totals) + sum(ProjectTool totals where already\_owned = false)

```



\* Project variance:



```

actual\_cost - estimated\_cost

```



\* Global totals:



&#x20; \* Material total = sum of all ProjectMaterial recorded\_price × quantity

&#x20; \* Tool total = sum of all purchased ProjectTool entries



\---



\### 5. Media Management



\* Media files are stored locally on disk under `/uploads/`



\* Each media record must store:



&#x20; \* `id`

&#x20; \* `project\_id`

&#x20; \* `file\_path`

&#x20; \* `type` (enum: receipt, progress, document, other)



\* Media can only be associated with a project (not materials/tools in MVP)



\---



\### 6. User Interface



\* Server-rendered UI using Flask + Jinja2

\* Required pages:



&#x20; \* Project list

&#x20; \* Project detail view

&#x20; \* Add/edit project form

&#x20; \* Add material/tool forms

\* No client-side frameworks



\---



\## Data Model Constraints



\* `quantity > 0`

\* `recorded\_price >= 0`

\* `unit\_price\_at\_time >= 0`

\* If `already\_owned = true`, tool cost must evaluate to 0

\* Materials and tools are global entities reused across projects



\---



\## Technical Constraints



\* Backend: Python + Flask

\* Frontend: Jinja2 templates (server-rendered)

\* Database: SQLite

\* File storage: local filesystem

\* API style: REST (internal use)



\---



\## Explicit Non-Goals (Out of Scope)



The following are not included in the MVP:



\### Authentication \& Users



\* No login system

\* No user accounts

\* Single-user application only



\### Advanced Infrastructure



\* No PostgreSQL

\* No cloud deployment requirements

\* No containerization



\### Performance \& Scaling



\* No optimization for large datasets

\* No caching

\* No concurrency handling



\### Analytics \& Reporting



\* No advanced dashboards

\* No historical trend analysis

\* No export functionality



\### Mobile \& UX Enhancements



\* No mobile app

\* No responsive design requirement

\* No frontend frameworks (React, etc.)



\### Advanced Relationships



\* No project hierarchies (sub-projects)

\* No linked/related projects

\* No material/tool usage analytics across projects



\---



\## Success Criteria



The MVP is complete when:



\* A user can create a project

\* A user can add materials and tools to a project

\* Costs are calculated correctly and displayed

\* Media can be uploaded and viewed per project

\* The application runs locally without errors



\---



\## Summary



This MVP delivers a minimal, fully functional project tracking system focused on:



\* cost tracking

\* project organization

\* simplicity of implementation



All features not directly supporting these goals are excluded.



