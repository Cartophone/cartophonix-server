from app import app

if __name__ == "__main__":
    app.run(host=app.config['SERVER_HOST'], port=app.config['SERVER_PORT'])