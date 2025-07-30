# Configuration file for ParkingPro
# This is where I put all the settings

import os

class Config:
    SECRET_KEY = 'my_super_secret_key_12345'  # change this in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TODO: add more config options later
    # like email settings, payment gateway, etc. 