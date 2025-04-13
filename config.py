# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///team_management.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False