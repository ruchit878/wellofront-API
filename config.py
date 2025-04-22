import os

DB_USER = os.getenv("DB_USER", "phpmyadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "NewPassword123%21")
DB_HOST = os.getenv("DB_HOST", "64.227.152.165")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "wellofront")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
