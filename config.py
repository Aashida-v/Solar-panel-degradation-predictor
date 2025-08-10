import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'users.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'aashida2023@gmail.com'
    MAIL_PASSWORD = 'hzeo tfzn dghv dhov'  # Use App Password for Gmail
