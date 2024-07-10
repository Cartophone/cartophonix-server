from flask import Flask
from config.config import SERVER_HOST, SERVER_PORT
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=SERVER_HOST, port=SERVER_PORT)