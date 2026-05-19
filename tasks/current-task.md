# Current Task
Add indexes and uniqueness constraints for core lookup paths

## Summary
Improve correctness and queryability of the schema.

## Acceptance Criteria
- Add unique constraints where needed, such as category names and optional merchant names if appropriate.
- Add indexes for common joins and filter fields:
  - project_id
  - material_id
  - tool_id
  - merchant_id
  - status
  - created_at
- Document rationale for each index.