from flask import Flask
from flasgger import Swagger
from .config import Config
from .extensions import db, jwt
from .routes.auth import auth_bp
from .routes.tasks import tasks_bp

SWAGGER_CONFIG = {
    'title': 'Task Manager API',
    'version': '1.0',
    'description': (
        'A RESTful API for task management with JWT authentication.\n\n'
        '**How to authenticate:**\n'
        '1. Register or login via `/api/auth/register` or `/api/auth/login`\n'
        '2. Copy the `token` from the response\n'
        '3. Click **Authorize** and enter: `Bearer <your_token>`'
    ),
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter: Bearer &lt;token&gt;',
        }
    },
    'security': [{'BearerAuth': []}],
    'uiversion': 3,
}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    Swagger(app, config={'specs_route': '/docs/', **SWAGGER_CONFIG}, merge=True)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

    return app
