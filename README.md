# TrekApp
 => WSA Project

<!-- travelapi.txt -->

**Features:**
 
| Database | HTTP Methods|
|:---------|------: 	 |
| Create   | POST   	 |
| Retrieve | GET   	 |
| Update   | PUT    	 |
| Delete   | DELETE 	 |		
	
	
### API Endpoints

=> **POST** http://127.0.0.1:5000/api/doLogin/

**Parameters:**

- email : required: Email of the registered user
- psw: required: Password of registered user

eg: Payload:
{
	"email": "your email",
	"psw": "your password"
}

**Response:**

- loggedin: Returns True or False based on login status
- message: A message after login is attempted
- token: A token to be used for authorization

=> **POST** http://127.0.0.1:5000/api/doRegister/

=> **GET** http://127.0.0.1:5000/api/treks/
- Response: JSON

=> POST http://127.0.0.1:5000/api/doAddTrek/

**Parameters:**

- title : required: text: Title of the trek
- days: required: number: Number of days required for the trek
- difficulty: required: text: Diffculty level
- total_cost: required: number: Total Cost

eg: Payload:
{
	"title": "your email",
	"days": <days>,
	"difficulty": "your password",
	"total_cost": <total_cost>,
}
  
**Response:**
	
- message: A message after trek addition is attempted

	
### Basic API Endpoints

1. Register => POST - /api/doRegister

2. Login => POST - /api/doLogin

3. All Treks => GET - /api/treks

4. Add Trek => POST - /api/doAddTrek

5. Update Trek => PUT - /api/doUpdateTrek

6. Delete Trek => DELETE - /api/doDeleteTrek


### REST Framework

**Resource: Treks**

1. All Treks => /api/treks => GET
2. Add Treks => /api/treks => POST
3. Update Treks => /api/treks => PUT
4. Delete Treks => /api/treks => DELETE


**Resource: Iternaries**

/rest/iternaries

1. GET /rest/iternaries
2. POST /rest/iternaries
3. PUT /rest/iternaries
4. DELETE /rest/iternaries
