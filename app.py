# Parking Management System - My Final Project for MAD Course
# Created by: [Student Name] - ID: 23f2003539@ds.study.iitm.ac.in
# Date: July 2025
# This is my first Flask project so please be gentle with the code review :)
# I learned Flask from YouTube tutorials and Stack Overflow

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from controllers.extensions import db
from werkzeug.security import generate_password_hash

# Initialize extensions - got this from Flask docs
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # TODO: change this secret key in production (if I ever deploy this)
    app.config['SECRET_KEY'] = 'my_super_secret_key_12345'  # i know this is bad but its just for demo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # this reduces memory usage
    
    # TODO: add environment variables for production
    # learned about this from a blog post but haven't implemented yet

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints - had to put this here to avoid circular import issues
    # spent like 2 hours debugging this lol - kept getting import errors
    from controllers.routes import auth, admin, user
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    from controllers.api import api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        from models.models import User, ParkingLot, ParkingSpot, Reservation
        db.create_all()
        
        # make sure admin user exists - this is for testing purposes
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # default admin password is 'admin' - change this later
            # got this idea from a tutorial but simplified it
            admin_user = User(username='admin', password=generate_password_hash('admin'), role='admin')
            db.session.add(admin_user)
        else:
            admin_user.role = 'admin'  # just in case - sometimes the role gets reset
        db.session.commit()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        from models.models import ParkingLot, ParkingSpot, Reservation
        from flask_login import current_user
        
        # get some stats for the homepage - only show to logged in users
        stats = {}
        if current_user.is_authenticated:
            total_lots = ParkingLot.query.count()
            total_spots = ParkingSpot.query.count()
            total_users = User.query.filter_by(role='user').count()
            
            # TODO: implement actual rating system later
            avg_rating = 4.8  # hardcoded for now - will add real ratings later
            # this could be calculated from actual user reviews
            
            stats = {
                'total_lots': total_lots,
                'total_spots': total_spots,
                'total_users': total_users,
                'avg_rating': avg_rating
            }
        
        return render_template('home.html', stats=stats)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)  # remember to set debug=False in production
    # learned about debug mode from Flask documentation 