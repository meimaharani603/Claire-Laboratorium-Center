import os
BASE_DIR = os.path.dirname(__file__)
class Config:
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "lab.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
