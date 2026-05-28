# Current Task
Implement project-tool association workflow

## Summary
Allow users to add a tool to a project with already-owned logic and project-specific pricing.

## Acceptance Criteria
- User can attach a tool to a project.
- Fields include quantity, already_owned, estimated_unit_price, actual_unit_price, notes, purchased_on, and merchant.
- Project detail page lists attached tools.
- If already_owned is true, actual cost contribution is excluded from totals.