# vendor-management-system
Developed a Vendor Management System using Django and Django REST Framework. This system handles vendor profiles, tracks purchase orders, and calculates vendor performance metrics.

## Steps to run the project:

1. Clone the repository
    `git clone https://github.com/Ats023/vendor-management-system.git`

2. Navigate to project directory
`cd vendor-management-system`

3. Set up virtual environment (recommended)
- Windows:
`py -m venv <name of virtual env>`
`<name of virtual env>\Scripts\activate.bat`
- macOS/Linux:
`python3 -m venv <name of virtual env>` 
`source <name of virtual env>/bin/activate`

4. Install dependencies
`pip install -r requirements`

5. Run migrations (recommended)
`py manage.py migrate`

6. Run tests
`py manage.py test vendors`

7. Run server
`py manage.py runserver`
