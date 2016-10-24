import app.endpoint.routes
import app.user.routes
import app.token.routes


blueprints = [
        app.endpoint.routes.blueprint,
        app.user.routes.blueprint,
        app.token.routes.blueprint
]
