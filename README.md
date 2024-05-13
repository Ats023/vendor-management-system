
# vendor-management-system
Developed a Vendor Management System using Django and Django REST Framework. This system handles vendor profiles, tracks purchase orders, and calculates vendor performance metrics.

## Steps to run the project:

1. Clone the repository\
    ```
    >> git clone https://github.com/Ats023/vendor-management-system.git
    ```

2. Navigate to project directory\
	```
	>> cd vendor-management-system
	```
3. Set up virtual environment (recommended)\
- Windows:
	```
	>> py -m venv <name of virtual env>
	>> <name of virtual env>\Scripts\activate.bat
	```
- macOS/Linux:
	```
	>> python3 -m venv <name of virtual env>
	>> source <name of virtual env>/bin/activate
	```
4. Install dependencies\
	```
	>> pip install -r requirements
	```
5. Run migrations (recommended)\
	```
	>> py manage.py migrate
	```
6. Run tests\
	```
	>> py manage.py test vendors
	```
7. Run server\
	```
	>> py manage.py runserver
	```
## Instructions on accessing API endpoints
All API endpoints are secured with token-based authentication and will return '401' (unauthorized) error when tried to access directly. During tests, an APIClient class is created with a token generated for the test user. This token is used in all headers, which allows the test client to access all API endpoints without issue.

To manually visit the urls, please use '#' to comment-out the following decorators before all functions:
```
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
```
