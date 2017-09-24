# Introduction
A companion for a client side developer, it's a mock server written in Flask that responds with JSON's.


Consider a situation where you working on single page application that consume RESTful API's and there is a new feature requires new endpoints to be added.
While the work on the endpoint is in progress by the backend team, you, as a client-side developer can create a mock of this endpoint as if it actually exist.


## Architecture
```
User creates mock endpoints in the UI, he may define methods, routes and
JavaScript code to be run when route is requested.
+------------+
|            | <------
|  UI        | ----- |
|            |     | |
+------------+     | |
                   | |
                   v |
             +--------------+
             |   API        |   API is responsible for providing the UI all
             |              |   information about the routes stored.
             |localhost:5000|
             +--------------+
                   |
                   |
                   |
                   v
             +------------+
             |            |    All this information stored in MongoDB.
             |  MongoDB   |
             |            |
             +------------+
                  |  ^
                  |  |
                  |  |
                  v  |
              +------------+
              |            |    A mock server.
              | MockServer |    On start up, it requests the information about
              |            |    defined routes and registers them in runtime.
              +------------+
                  ^  |           When route matched, the mock server sends the
                  |  |           code associated with this route to JSE server.
                  |  |           The result of this operation is saved to MongoDB
                  |  |           and returned to the user requested this route.
                  |  |
                  |  |
                  |  |
                  |  -------> +------------+
                  |           |            |  JSE is a server running on ExpressJS
                  ----------> |  JSE       |  that executes JavaScript code and
                              |            |  returns a result in JSON.
                              +------------+
```

## Setup
```
$ git clone https://github.com/vladimirze/Gimme-JSON-backend.git
$ cd Gimme-JSON-backend
$ virtualenv .virtualenv
$ . .virtualenv/bin/activate
$ pip install -r requirements.txt
$ sudo docker run --name gimmejson-mongo -d mongo
```

Lets create .env file to store database host, password and secret key (see explanation below):
```
export GIMMEJSON_SECRET_KEY="YOUR_SECRET_KEY"
export GIMMEJSON_DATABASE_HOST=localhost
export GIMMEJSON_DATABASE_PORT=27017
```

Note that, .env is ignored by git intentionally, credentials should not be commited.

Next step is generating application secret key. Authentication (JWT is used as authentication mechanism) is set to `False` by default (see `IS_AUTH_REQUIRED` flag in `settings.py`), however it's still needed for unit tests, so, if you don't want authentication or don't plan to run unit tests skip this.

Secret key is used for token validation.

```
$ python manage.py generatesecret
abcde...whatever
```

Run `$ . .env` to set the environment variables.  
Start the server by running `$ python manage.py runserver`.

**User creation and authentication**  
If you enabled authentication, we should create new user.

```
$ curl -H "Content-Type: application/json" -X POST -d '{"username": "developer", "password": "developer"}' http://localhost:5000/user/
-> {}
```
**Getting a token**
```
$ curl -H "Content-Type: application/json" -X POST -d '{"username": "developer", "password": "developer"}' http://localhost:5000/token/`
-> `{"token": "token"}`
```

All requests should include the authorization token in header `Authorization: JWT token` when sending requests:

```
$ curl -H "Content-Type: application/json" -H "Authorization: JWT token" -X GET http://localhost:5000/endpoint/
```

## Tests
**Switch to test environment**  
To switch to test environment just edit settings variable in `settings.py` to look like this:
`settings = Testing`  
In this case, authentication will be enabled and also different database name will be used.

**Running all the tests**
```
$ python manage.py test
```

**Running tests only for given module**
```
$ python manage.py test -m test_endpoint
```

**Running tests only for given class in a module**
```
$ python manage.py test -m test_endpoint -c EndpointPOST
```

**Running a single unit test**
```
$ python manage.py test -m test_endpoint -c EndpointPOST -t test_create_new_endpoint
```

**Running tests before commit**  
Copy `pre-commit` file to `.git/hooks` and run `chmod +x pre-commit` to make it executable.


## Endpoints
### Storage
| Method              | Endpoint                                     |
|---------------------|----------------------------------------------|
| GET, DELETE         | http://localhost:5000/storage/[storage_id]/  |
| GET, POST           | http://localhost:5000/storage/               |


#### Example
POST http://localhost:5000/storage/
```
{
	"value": "[]"
}
```

**Response**  
```
{
	"value": "[]",
	"_id": "59c682a7eceefb25eb388b38"
}
```


### Endpoint
| Method                   | Endpoint                                      |
|--------------------------|-----------------------------------------------|
| GET, DELETE, PUT, PATCH  | http://localhost:5000/endpoint/[endpoint_id]  |
| GET, POST                | http://localhost:5000/endpoint/               |

#### Example
POST http://localhost:5000/endpoint  
```
{
	"on_get": "$g.setResponse(200, $g.storage.people);",
	"on_post": "$g.storage.people.push($g.payload); $g.setResponse(200, $g.payload);",
	"on_patch": "",
	"on_delete": "",
	"route": "/something",
	"on_put": "",
	"storage": [
		"people"
	]
}
```

**Response**  
```
{
	"value": "[]",
	"_id": "59c682a7eceefb25eb388b38"
}
```


### Token
| Method  | Endpoint                      |
|---------|-------------------------------|
| POST    | http://localhost:5000/token/  |

#### Example
POST http://localhost:5000/token  
```
{
	"username": "developer",
	"password": "developer"
}
```

**Response**  
```
{
	"token": "..."
}
```

### User
| Method  | Endpoint  |
|---------|-----------|
| POST    | http://localhost:5000/user/  |


## Common Development Tasks
**Access MongoDB shell**  
```
$ sudo docker run -it --link gimmejson-mongo:mongo --rm mongo sh -c 'exec mongo "172.17.0.2:27017/test"'
```
