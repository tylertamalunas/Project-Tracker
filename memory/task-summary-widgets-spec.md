# Task Complete: Summary Widgets Specification

## Date
2025-05-15

## Task
Specify which totals and summary widgets appear in the first release.

## Decisions Made

### Project Detail Page
- Shows: estimated total, actual total, variance
- Variance color-coded (red = over, green = under)
- Tools with `already_owned = true` contribute $0

### Dashboard
- 4 summary cards: total projects, active projects, completed projects, total actual spend
- Recent projects list (up to 5, prioritizing active projects)
- Global spend broken into materials vs purchased tools
- **No budget overrun alerts** — excluded as "advanced dashboard" per MVP scope

### Project List
- Per-row totals (estimated, actual, variance) — already implemented
- No page-level aggregates

### Global Summaries
- All-time material spend: SUM of all project_materials actual costs
- All-time tool spend: SUM of all project_tools actual costs where not already_owned

## File Created
- `Instructions/summary-widgets-spec.md` — full specification with formulas and data sources

## What's NOT in MVP
- Category breakdowns, trend charts, alerts, export, forecasting
