import app.resource.routes
import app.server.routes
import app.user.routes
import app.token.routes


blueprints = [
        app.resource.routes.blueprint,
        app.server.routes.blueprint,
        app.user.routes.blueprint,
        app.token.routes.blueprint
]
