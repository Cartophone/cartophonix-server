from app import app
import logging
from config.config import SERVER_HOST, SERVER_PORT
from waitress import serve

logging.basicConfig(level=logging.INFO)
logging.info(f"Starting server at http://{SERVER_HOST}:{SERVER_PORT}")

serve(app, host=SERVER_HOST, port=SERVER_PORT)