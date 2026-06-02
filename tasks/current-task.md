# Current Task
Implement local media upload storage service

## Summary
Build local file handling for receipts, documents, and reference photos.

## Acceptance Criteria
- Uploaded files are saved in a predictable local directory structure.
- File metadata is saved to the `media` table.
- Unsafe filenames are normalized.
- App can serve or download saved files in development.