# Database models for parking system
# I used SQLAlchemy because it's easier than raw SQL
# Learned this from the Flask tutorial and some YouTube videos
# Had to look up the relationship syntax on Stack Overflow

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from controllers.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # admin or user
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    # TODO: add email field later - maybe for password reset functionality

    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = password
        self.role = role  # can be 'admin' or 'user'
        # could add more fields later like email, phone, etc.

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(150), nullable=False)  # like "Downtown Mall Parking"
    price = db.Column(db.Float, nullable=False)  # price per hour - could be per day later
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)  # for security - might change this later
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan')

    def __init__(self, prime_location_name, price, address, pin_code, maximum_number_of_spots):
        self.prime_location_name = prime_location_name
        self.price = price
        self.address = address
        self.pin_code = pin_code
        self.maximum_number_of_spots = maximum_number_of_spots
        # might add more fields like description, image_url later

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A=Available, O=Occupied
    reservations = db.relationship('Reservation', backref='spot', lazy=True)

    def __init__(self, lot_id, status='A'):
        self.lot_id = lot_id
        self.status = status
        # A = Available, O = Occupied - could use enum later

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)  # null until user leaves
    parking_cost = db.Column(db.Float, nullable=True)  # calculated when leaving

    def __init__(self, spot_id, user_id, parking_timestamp=None, leaving_timestamp=None, parking_cost=None):
        self.spot_id = spot_id
        self.user_id = user_id
        self.parking_timestamp = parking_timestamp or datetime.utcnow()
        self.leaving_timestamp = leaving_timestamp
        self.parking_cost = parking_cost
        # parking_cost is calculated when user leaves the spot 