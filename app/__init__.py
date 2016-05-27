import app.endpoint.routes
import app.server.routes
import app.user.routes
import app.token.routes


blueprints = [
        app.endpoint.routes.blueprint,
        app.server.routes.blueprint,
        app.user.routes.blueprint,
        app.token.routes.blueprint
]
