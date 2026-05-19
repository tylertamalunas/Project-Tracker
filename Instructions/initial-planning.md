**Overview/Objective:**

I want to create a web app. The primary intended audience is homeowners. The purpose is to create an application that tracks materials, costs, and tools used for the project. It is intended to be used as a planning tool and an after completion summary. This provides an all-in-one location to store project data and costs for individuals.



**Goals and Use Cases:**

* Plan projects before starting
* Track initial estimated costs and materials vs actual expenditure
* store receipts and reference photos
* reuse past project data for future planning



**Target Audience:**

Homeowners, DIYers



**Feature Requirements:**

* **Project Management:**

  * CRUD projects
  * track sub-projects
  * link related projects
  * store notes, documents, and images
  * total cost tracking
* **Project Inventory:**

  * add materials to project
  * add tools to project
  * quantity + cost per project
  * tool ownership flag (owned vs purchased)
* **Materials Management:**

  * CRUD materials
  * Global material catalog
  * price tracking
  * usage tracking across projects
  * merchant tracking notes (string)
* **Tools Management**

  * owned vs purchased per project
  * cost behavior
* **Financial Tracking:**

  * Calculating total costs

    * total project cost = sum(materials + tools costs)
    * total all time spent = sum(total project costs)
    * material total (global) = sum of all projectMaterial recorded\_price
    * tool total (global) = sum of all purchased projectTool recorded\_price
    * project variance = actual cost - estimated cost
  * handling 0$ "already owned" logic

    * if marked "owned", price excluded from project total
  * prices calculated dynamically



**User Flows:**

1. user creates project
2. adds materials to project (new or from global catalog)
3. adds tools (specifies if purchased or owned)
4. uploads receipts, documents, images
5. tracks costs over time
6. marks project complete



**Data Model:**

* **Constraints:**

  * recorded\_price must be >= 0
  * quantity must be > 0
  * if already\_owned = true → recorded\_price = 0



* Entities

  * project
  * material
  * tool
  * projectMaterial (join table)
  * projectTool (join table)
  * media
* Relationships

  * materials are global
  * tools are global
  * projects reference both
* **Schema:**

  * ProjectMaterial (Join Table)

    * project\_id (FK)
    * material\_id (FK)
    * quantity (int)
    * recorded\_price (float - locked in at time of use)
  * ProjectTool (Join Table)

    * project\_id (FK)
    * tool\_id (FK)
    * already\_owned (Boolean)
    * unit\_price\_at\_time (float)
    * quantity (int)
  * Project:

    * &#x20; id
    * &#x20; name
    * &#x20; description
    * &#x20; created\_at
  * Material:

    * &#x20; id
    * &#x20; name
    * &#x20; default\_price
    * last\_used\_price
  * Tool:

    * &#x20; id
    * &#x20; name
    * &#x20; default\_price
    * last\_used\_price
  * Media:

    * &#x20; id
    * &#x20; project\_id
    * &#x20; file\_path
    * &#x20; type (enum: receipt, progress, document, other)



**Technical Specifications:**

* written in Python with Flask framework
* Flask + server-rendered frontend templates (Jinja2)
* SQLite database
* API style: REST
* File storage: local





**MVP Scope:**

* no auth
* No concurrency concerns (since single user)
* create projects
* add materials/tools
* track cost
* simple UI
* locally stored data
* performance not critical



**Future Scope:**

1. authentication
2. PostgreSQL migration
3. containerization
4. performance
5. analytics
6. mobile version

