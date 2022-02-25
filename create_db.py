from dotenv import load_dotenv

load_dotenv()

from app_modules import db, create_app

db.create_all(app = create_app())