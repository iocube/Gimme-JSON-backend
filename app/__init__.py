import resource.routes
import server.routes
import user.routes


blueprints = [
        resource.routes.blueprint,
        server.routes.blueprint,
        user.routes.blueprint
]
