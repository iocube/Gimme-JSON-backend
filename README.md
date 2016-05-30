Status: In development.

#### Gimme-JSON backend
A companion for a front end developer.

#### Dependencies
Flask
MongoDB
virtualenv

#### Running
##### Mongo daemon
$ sudo mongod

##### Project dependencies
$ pip install -r requirements.txt

##### Switching to development environment
$ . settings.sh development

##### Generating application secret key
Secret key used for token validation (authentication) therefore it must kept outside of the codebase.

$ python manage.py generatesecret
`abcde...whatever`

$ export GIMMEJSON_SECRET_KEY="abcde...whatever"

##### Starting the development server
$ python manage.py runserver

#### Tests
#### Switch to test environment
$ . settings.sh testing

##### Run all tests
$ python manage.py test

##### Run by module
$ python manage.py test -m test_endpoint

##### Run by class
$ python manage.py test -m test_endpoint -c EndpointPOST

##### Run single test
$ python manage.py test -m test_endpoint -c EndpointPOST -t test_create_new_endpoint

##### Running tests before commit
Copy 'pre-commit' file to `.git/hooks` and run `chmod +x pre-commit` to make it executable.

#### User creation and authentication
To start working with Gimme-JSON a new user has to be created since only authenticated users are accepted.

##### Creating a new user
POST `localhost:5000/user/`
{"username": "abrakadabra", "password": "12345678"}

##### Obtaining a token
POST `localhost:5000/token/`
{"username": "abrakadabra", "password": "12345678"}
Response: {"token": "abcde...pinguins"}

##### Authentication
Once the token is obtained, from now on it must be included in headers when making requests.
`Authorization: JWT abcde...penguins`

#### Usage example
##### Creating a new endpoint
POST `localhost:5000/endpoint/`
{
    "endpoint": "/api/v1/cats",
    "methods": ["GET"],
    "response": "[{\"id\": 1, \"name\": \"Mr.Cat\"},{\"id\": 2, \"name\": \"Mrs.Cat\"}]"
}

##### Creating another endpoint
POST `localhost:5000/endpoint/`
{
    "endpoint": "/api/v1/cats/<int:id>/",
    "methods": ["GET"],
    "response": "{\"id\": \"1\"}"
}

##### Restarting the server to take changes
After you have created new endpoints you should restart the server so that you can interact with your endpoints,
therefore there is endpoint for that!
DELETE `localhost:5000/server/` (nope, it will not self-destroy the server, trust me)
