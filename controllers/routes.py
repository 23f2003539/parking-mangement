# Routes for the parking system
# This file handles all the web routes - admin, user, and auth
# I split it into blueprints to keep things organized
# Got this idea from a Flask tutorial but modified it for my needs

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import ParkingLot, ParkingSpot, Reservation, User
from controllers.extensions import db
from datetime import datetime

# Admin Blueprint - handles all admin stuff
admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # check if user is actually admin
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    
    # get some stats for the dashboard
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    total_revenue = 0  # money made so far - this could be improved later
    
    # calculate money made from parking
    completed_reservations = Reservation.query.filter(Reservation.leaving_timestamp.isnot(None)).all()
    for reservation in completed_reservations:
        total_revenue += reservation.parking_cost or reservation.spot.lot.price or 0
    
    # get recent activity for the feed (max 5 items)
    recent_activity = []
    
    # get recent bookings (3 max) - this shows what's happening lately
    recent_reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).limit(3).all()
    
    # add bookings to activity - this could be done better but it works
    for reservation in recent_reservations:
        recent_activity.append({
            'type': 'booking',
            'message': f'User {reservation.user.username} booked spot {reservation.spot.id} at {reservation.spot.lot.prime_location_name}',
            'timestamp': reservation.parking_timestamp,
            'icon': 'fas fa-car',
            'color': 'text-primary'
        })
    
    # add recent lot creations (2 max to keep total at 5)
    recent_lots = ParkingLot.query.order_by(ParkingLot.id.desc()).limit(2).all()
    for lot in recent_lots:
        recent_activity.append({
            'type': 'lot_created',
            'message': f'New parking lot "{lot.prime_location_name}" added',
            'timestamp': datetime.utcnow(),  # using current time since no creation timestamp
            'icon': 'fas fa-building',
            'color': 'text-success'
        })
        # TODO: add proper creation timestamps to the database model
    
    # sort by time and limit to 5
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_activity[:5]
    # this sorting could be done in the database query but this is simpler
    
    return render_template('admin_dashboard.html', 
                         admin=current_user,
                         total_lots=total_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         total_revenue=total_revenue,
                         recent_activity=recent_activity)

@admin.route('/admin/lots')
@login_required
def admin_lots():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lots = ParkingLot.query.all()
    return render_template('admin_lots.html', lots=lots)

@admin.route('/admin/lots/create', methods=['GET', 'POST'])
@login_required
def create_lot():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('prime_location_name')
        price = request.form.get('price')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        max_spots_str = request.form.get('maximum_number_of_spots')
        
        # validate all fields are filled
        if not all([name, price, address, pin_code, max_spots_str]):
            flash('All fields are required.')
            return redirect(url_for('admin.create_lot'))
        if max_spots_str is None or price is None:
            flash('Invalid input for spots or price.')
            return redirect(url_for('admin.create_lot'))
        try:
            max_spots = int(max_spots_str)
            price = float(price)
        except ValueError:
            flash('Invalid number for spots or price.')
            return redirect(url_for('admin.create_lot'))
        # this validation could be better but it works for now
        lot = ParkingLot(prime_location_name=name, price=price, address=address, pin_code=pin_code, maximum_number_of_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        
        # create parking spots for this lot
        for i in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot created successfully!')
        return redirect(url_for('admin.admin_lots'))
    return render_template('admin_create_lot.html')

@admin.route('/admin/lots/<int:lot_id>/spots')
@login_required
def view_spots(lot_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    return render_template('admin_view_spots.html', lot=lot, spots=spots)

@admin.route('/admin/lots/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form.get('prime_location_name')
        lot.price = float(request.form.get('price'))
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')
        db.session.commit()
        flash('Parking lot updated successfully!')
        return redirect(url_for('admin.admin_lots'))
    return render_template('admin_edit_lot.html', lot=lot)

@admin.route('/admin/lots/<int:lot_id>/delete', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = any(spot.status == 'O' for spot in lot.spots)
    if occupied_spots:
        flash('Cannot delete lot: Some spots are occupied.')
        return redirect(url_for('admin.admin_lots'))
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin.admin_lots'))

@admin.route('/admin/lots/<int:lot_id>/summary')
@login_required
def lot_summary(lot_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    lot = ParkingLot.query.get_or_404(lot_id)
    spot_ids = [spot.id for spot in lot.spots]
    reservations = Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).all()
    revenue = sum(r.parking_cost or lot.price for r in reservations if r.parking_cost or lot.price)
    booking_count = len(reservations)
    bookings = [
        {
            'username': r.user.username if r.user else 'Unknown',
            'parking_timestamp': r.parking_timestamp.strftime('%Y-%m-%d %H:%M'),
            'leaving_timestamp': r.leaving_timestamp.strftime('%Y-%m-%d %H:%M') if r.leaving_timestamp else None
        }
        for r in reservations
    ]
    spots_info = [
        {
            'id': spot.id,
            'number': idx + 1,
            'status': 'Booked' if spot.status == 'O' else 'Available'
        }
        for idx, spot in enumerate(lot.spots)
    ]
    map_data = {
        'total_spots': lot.maximum_number_of_spots,
        'spots': spots_info
    }
    return jsonify({
        'revenue': revenue,
        'booking_count': booking_count,
        'bookings': bookings,
        'map_data': map_data,
        'lot_name': lot.prime_location_name
    })

@admin.route('/admin/edit_admin_info', methods=['POST'])
@login_required
def edit_admin_info():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('admin.admin_dashboard'))
    username = request.form.get('username')
    password = request.form.get('password')
    if username:
        current_user.username = username
    if password:
        current_user.password = generate_password_hash(password)
    db.session.commit()
    flash('Admin info updated successfully!')
    return redirect(url_for('admin.admin_dashboard'))

# Auth Blueprint - handles login/register

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # check if fields are filled
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('auth.register'))
        
        # check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        # create new user - hash the password for security
        # learned about password hashing from a security tutorial
        new_user = User(username=username, password=generate_password_hash(password), role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('auth.login'))
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('auth.login'))

# User Blueprint - handles user stuff

user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    
    # get user's booking stats
    user_reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    total_bookings = len(user_reservations)
    active_bookings = len([r for r in user_reservations if not r.leaving_timestamp])  # bookings that are still active
    # this could be optimized with a database query but it works for now
    
    # calculate how much money they spent
    total_spent = 0
    for reservation in user_reservations:
        if reservation.leaving_timestamp:  # only completed bookings
            total_spent += reservation.parking_cost or reservation.spot.lot.price or 0
    # this calculation could be more sophisticated but it works for now
    
    # get number of available lots
    available_lots = ParkingLot.query.count()
    
    # get recent bookings - limit to 5 to keep the page fast
    last_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.parking_timestamp.desc()).limit(5).all()
    
    # TODO: add pagination for reservations later
    
    return render_template('user_dashboard.html', 
                         user=current_user, 
                         last_reservations=last_reservations,
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         total_spent=total_spent,
                         available_lots=available_lots)

@user.route('/user/lots')
@login_required
def user_lots():
    if current_user.role != 'user':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lots = ParkingLot.query.all()
    return render_template('user_lots.html', lots=lots)

@user.route('/user/lots/<int:lot_id>/book', methods=['POST'])
@login_required
def book_spot(lot_id):
    if current_user.role != 'user':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
    if not spot:
        flash('No available spots in this lot.')
        return redirect(url_for('user.user_lots'))
    spot.status = 'O'
    reservation = Reservation(spot_id=spot.id, user_id=current_user.id, parking_timestamp=datetime.utcnow())
    db.session.add(reservation)
    db.session.commit()
    flash(f'Spot {spot.id} booked successfully!')
    return redirect(url_for('user.reservations'))

@user.route('/user/reservations')
@login_required
def reservations():
    if current_user.role != 'user':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('user_reservations.html', reservations=reservations)

@user.route('/user/reservations/<int:reservation_id>/release', methods=['POST'])
@login_required
def release_spot(reservation_id):
    if current_user.role != 'user':
        flash('Access denied.')
        return redirect(url_for('auth.login'))
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id or reservation.leaving_timestamp:
        flash('Invalid operation.')
        return redirect(url_for('user.reservations'))
    spot = ParkingSpot.query.get(reservation.spot_id)
    if not spot:
        flash('Spot not found.')
        return redirect(url_for('user.reservations'))
    spot.status = 'A'
    reservation.leaving_timestamp = datetime.utcnow()
    db.session.commit()
    flash('Spot released successfully!')
    return redirect(url_for('user.reservations')) 