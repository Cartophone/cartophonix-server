from app import app
from config.config import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)