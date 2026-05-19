# Summary Widgets & Totals — MVP Specification

## Purpose

Define the exact metrics, data sources, and placement of all summary/total widgets in the first release.

---

## 1. Project Detail Page (`/projects/<id>`)

### Summary Section

Displayed at the top of the project detail view, below the project metadata.

| Metric | Formula | Data Source |
|--------|---------|-------------|
| Estimated Total | `SUM(project_materials.quantity × project_materials.estimated_unit_price)` + `SUM(project_tools.quantity × project_tools.estimated_unit_price WHERE already_owned = false)` | `PROJECT_MATERIALS` + `PROJECT_TOOLS` for this project |
| Actual Total | `SUM(project_materials.quantity × project_materials.actual_unit_price)` + `SUM(project_tools.quantity × project_tools.actual_unit_price WHERE already_owned = false)` | `PROJECT_MATERIALS` + `PROJECT_TOOLS` for this project |
| Variance | `actual_total - estimated_total` | Computed from above |

### Display Rules

- Variance is color-coded: red if positive (over budget), green if negative (under budget), neutral if zero
- If `actual_unit_price` is NULL for a line item, that item contributes $0 to the actual total
- Tools where `already_owned = true` contribute $0 to both estimated and actual totals

---

## 2. Project List Page (`/projects`)

### Per-Row Totals

Each project row shows:

| Column | Formula | Source |
|--------|---------|--------|
| Estimated Total | Same as project detail estimated total | Computed per project |
| Actual Total | Same as project detail actual total | Computed per project |
| Variance | `actual_total - estimated_total` | Computed |

No page-level aggregate totals on the project list page in MVP.

---

## 3. Dashboard Page (`/`)

### Summary Cards

| Card | Metric | Data Source |
|------|--------|-------------|
| Total Projects | `COUNT(projects)` | `PROJECTS` table |
| Active Projects | `COUNT(projects WHERE status = 'active')` | `PROJECTS` table |
| Completed Projects | `COUNT(projects WHERE status = 'completed')` | `PROJECTS` table |
| Total Actual Spend | `SUM(all project actual totals)` | Aggregated from `PROJECT_MATERIALS` + `PROJECT_TOOLS` across all projects |

### Recent Projects List

- Shows the 5 most recently created or updated projects
- Columns: name, status, actual total
- Links to project detail page

### Decision: Budget Overrun Alerts

**Not included in MVP.** Rationale:
- The MVP scope explicitly excludes "advanced dashboards" and "historical trend analysis"
- Variance is already visible on the project list and project detail pages
- Adding alert logic increases complexity without matching a stated requirement

### Decision: Recent Projects

**Included.** The page-map already specifies "recent or active projects list" on the dashboard. Implementation:
- Show up to 5 projects, ordered by `updated_at DESC`
- Filter to `active` status first; if fewer than 5, backfill with `planned` projects

---

## 4. Global Spend Summaries (Dashboard)

### Metrics

| Metric | Formula | Data Source |
|--------|---------|-------------|
| All-Time Material Spend | `SUM(project_materials.quantity × project_materials.actual_unit_price)` across all projects | `PROJECT_MATERIALS` table |
| All-Time Purchased Tool Spend | `SUM(project_tools.quantity × project_tools.actual_unit_price WHERE already_owned = false)` across all projects | `PROJECT_TOOLS` table |

### Display

- Shown as part of the "Total Actual Spend" card, with a breakdown tooltip or sub-line:
  - Materials: $X
  - Tools: $Y
  - Total: $X + $Y

---

## 5. What Is NOT Included in MVP

- Per-category spend breakdowns
- Monthly/weekly spend trends
- Budget overrun alerts or notifications
- Comparison charts (estimated vs actual)
- Export of summary data
- Spend forecasting

---

## 6. Implementation Notes

- All totals are computed dynamically (no stored/cached totals)
- The `Project.estimated_total`, `Project.actual_total`, and `Project.variance` properties on the model handle per-project calculations
- Dashboard global metrics will query across all `ProjectMaterial` and `ProjectTool` rows
- For MVP scale (single user, local), N+1 query patterns are acceptable; optimize later if needed
