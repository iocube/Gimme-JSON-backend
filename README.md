# Introduction
A companion for a client side developer, it's a fake backend written in Flask that responds with static JSON data.  

This tool might be helpful in situations where you working on client-side, for example, building single page application that consumes some RESTful API's and there is a new feature requires new endpoints to be added, while work on the endpoints is in progress by the backend team, you, as a client-side developer can try to create a mock as if the endpoints actually exist.

You can run it as docker service, see [Gimme-JSON-docker repository](https://github.com/iocube/Gimme-JSON-docker).

## Dependencies
- Flask
- MongoDB
- virtualenv

## Running
```
$ mongod
$ git clone <project>
$ cd <project>
$ virtualenv .virtualenv
$ . .virtualenv/bin/activate
$ pip install -r requirements.txt
```

## Creating .env file
.env file is used to store sensitive data, see .env.example as an example.  
`$ cp .env.example .env`

## Generating application secret key
Authentication is set to `False` by default (see `IS_AUTH_REQUIRED` flag in `settings.py`), however it's still needed for unit tests, so, if you don't want authentication or don't plan to run unit tests skip this.  

Currently JWT authentication is supported.  

Secret key is used for token validation (authentication), it should be kept outside of codebase, therefore assign it to `GIMMEJSON_SECRET_KEY` variable inside `.env` file.  

`$ python manage.py generatesecret`
`abcde...whatever`

## Reading configuration from .env
`$ . .env`

## Starting the development server
`$ python manage.py runserver`

Now, the server is running on localhost:5000.

## User creation and authentication
If you enabled authentication, to start working, new user has to be created.

## Creating a new user
`$ curl -H "Content-Type: application/json" -X POST -d '{"username": "abrakadabra", "password": "12345678"}' http://localhost:5000/user/`

Response:  
`{}`

## Obtaining a token
`$ curl -H "Content-Type: application/json" -X POST -d '{"username": "abrakadabra", "password": "12345678"}' http://localhost:5000/token/`


Response:  
`{"token": "some.long.token"}`

## Authentication
Once the token is obtained, from now on it must be included in headers when making requests:   
`Authorization: JWT abcde...penguins`

`$ curl -H "Content-Type: application/json" -H "Authorization: JWT some.long.token" -X GET http://localhost:5000/endpoint/`

## Tests
### Switching to test environment
To switch to test environment just edit settings variable in `settings.py` to look like this:
`settings = Testing`  
In this case, authentication will be enabled and also different database name will be used.

### Running all tests
`$ python manage.py test`

### Running by module
`$ python manage.py test -m test_endpoint`

### Running by class
`$ python manage.py test -m test_endpoint -c EndpointPOST`

### Running single test
`$ python manage.py test -m test_endpoint -c EndpointPOST -t test_create_new_endpoint`

### Running tests before commit
Copy 'pre-commit' file to `.git/hooks` and run `chmod +x pre-commit` to make it executable.

## Examples
### Creating a new endpoint
`$ curl -H "Content-Type: application/json" -X POST -d '{"endpoint": "/api/v1/animals", "methods": ["GET"], "response": "[{\"id\": 1, \"name\": \"cat\"}]"}' http://localhost:5000/endpoint/`

Response:  
`{"_id": "57af4368eceefb08b48d5fd5", "endpoint": "/api/v1/animals", "response": "[{\"id\": 1, \"name\": \"cat\"}]", "methods": ["GET"]}`

### Restarting the server to take changes
When you create new endpoints you should restart the server so that you can interact with your endpoints, therefore there is an endpoint for that!
DELETE `localhost:5000/server/` (nope, it will not self-destroy the server, trust me)
`$ curl -H "Content-Type: application/json" -X DELETE http://localhost:5000/server/`

### Get new endpoint
`$ curl -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/animals`

Response:  
`[{"name": "cat", "id": 1}]`

### Get list of all endpoints
`$ curl -H "Content-Type: application/json" -X GET http://localhost:5000/endpoint/`

### Change response of an endpoint
`$ curl -H "Content-Type: application/json" -X PUT -d '{"endpoint": "/api/v1/animals", "methods": ["GET"], "response": "[{\"id\": 1, \"name\": \"cat\"}, {\"id\": 2, \"name\": \"dog\"}]"}' http://localhost:5000/endpoint/57af4368eceefb08b48d5fd5/`

Response:  
`{"methods": ["GET"], "_id": "57af4368eceefb08b48d5fd5", "endpoint": "/api/v1/animals", "response": "[{\"id\": 1, \"name\": \"cat\"}, {\"id\": 2, \"name\": \"dog\"}]"}`

### Available endpoints
```
Create          POST,OPTIONS         http://localhost/endpoint/
Delete          DELETE,OPTIONS       http://localhost/endpoint/[endpoint_id]/
List            HEAD,GET,OPTIONS     http://localhost/endpoint/
Partial Update  PATCH,OPTIONS        http://localhost/endpoint/[endpoint_id]/
Modify          PUT,OPTIONS          http://localhost/endpoint/[endpoint_id]/
Restart         DELETE,OPTIONS       http://localhost/server/
New Token       POST,OPTIONS         http://localhost/token/
New User        POST,OPTIONS         http://localhost/user/
```

## Development
### Download MongoDB container
$ sudo docker run --name gimmejson-mongo -d mongo

### Access MongoDB shell
$ sudo docker run -it --link gimmejson-mongo:mongo --rm mongo sh -c 'exec mongo "172.17.0.2:27017/test"'

### Restart container
$ sudo docker restart gimmejson-mongo
