import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# IMPLEMENT DATABASE URL

class DatabaseURI:

    #DB config params
    DATABASE_NAME = "fyyur_dev"
    username = 'postgres'
    password = 'Iso#2009'
    url = '127.0.0.1:5432'
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)


