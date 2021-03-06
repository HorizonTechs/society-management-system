from os import getenv

SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL').replace("postgres://", "postgresql://")
SECRET_KEY = getenv('SECRET_KEY')
PASSWORD_RESET_KEY = getenv('PASSWORD_RESET_KEY')
CAP_KEY = getenv('CAP_KEY')