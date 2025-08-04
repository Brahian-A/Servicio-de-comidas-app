class Config:
    SECRET_KEY = "super-secret-key"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@localhost/hbnb_db"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"