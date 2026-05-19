# Data Model

Core tables:
- projects
- materials
- tools
- project_materials
- project_tools
- media_uploads

Important rules:
- Project totals are calculated from related materials, not manually entered
- Completed projects are read-only unless changed back to active
- Uploaded files are stored locally