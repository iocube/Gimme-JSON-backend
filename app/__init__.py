import resource.routes
import server.routes
import user.routes
import token.routes


blueprints = [
        resource.routes.blueprint,
        server.routes.blueprint,
        user.routes.blueprint,
        token.routes.blueprint
]
