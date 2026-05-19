## Project Statuses and Lifecycle Rules

### Allowed Status Values

* `planned`
* `active`
* `completed`

### Status Transitions

* `planned` → `active`
* `active` → `completed`
* `completed` → `active` (project can be reopened)

### Date Rules

* `start_date` is optional
* `end_date` is optional
* Dates are informational only in the MVP and are not enforced by status

### Completed Project Behavior (UI + Logic)

* Completed projects remain visible in the project list
* Completed projects display a green "Completed" status indicator
* Completed projects can be opened and viewed normally
* Completed projects are read-only:

  * cannot edit project details
  * cannot add/edit/remove materials
  * cannot add/edit/remove tools
  * cannot upload or modify media
* A completed project can be made editable again by changing status back to `active`

### Notes

* Status is the primary driver of project editability
* No additional states (e.g., `on_hold`, `archived`) are included in MVP
