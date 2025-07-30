# API endpoints for the parking system
# This is for future mobile app integration (if I ever make one)
# Using REST API style - learned this from a web development course
# Not fully implemented yet but the structure is there

from flask import Blueprint, jsonify, request
from models.models import ParkingLot, ParkingSpot, Reservation, User
from controllers.extensions import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

# get all parking lots - for mobile app
@api_bp.route('/parking-lots', methods=['GET'])
def get_parking_lots():
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        # count available spots
        available_spots = sum(1 for spot in lot.spots if spot.status == 'A')
        result.append({
            'id': lot.id,
            'location': lot.prime_location_name,
            'price': lot.price,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'available_spots': available_spots,
            'total_spots': len(lot.spots)
        })
    return jsonify(result)

# get spots in a specific lot
@api_bp.route('/parking-lot/<int:lot_id>/spots', methods=['GET'])
def get_parking_spots(lot_id):
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return jsonify([{'id': s.id, 'status': s.status} for s in spots])

# make a reservation - not fully implemented yet
# this is just a basic version - would need more error handling
@api_bp.route('/reserve', methods=['POST'])
def make_reservation():
    data = request.get_json()
    user_id = data.get('user_id')
    spot_id = data.get('spot_id')
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%d %H:%M:%S')

    spot = ParkingSpot.query.get(spot_id)
    if spot.status != 'A':
        return jsonify({'error': 'Spot already occupied'}), 400

    reservation = Reservation(user_id=user_id, spot_id=spot_id,
                              start_time=start_time, end_time=end_time)
    spot.status = 'O'
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation successful', 'reservation_id': reservation.id})

# get user's reservations
@api_bp.route('/user/<int:user_id>/reservations', methods=['GET'])
def get_user_reservations(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    result = []
    for r in reservations:
        result.append({
            'id': r.id,
            'spot_id': r.spot_id,
            'lot_id': r.spot.lot_id,
            'start_time': r.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': r.end_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)
