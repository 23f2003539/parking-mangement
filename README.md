# ParkingPro - Smart Parking Management System

## Project Overview
This is my final project for the MAD (Mobile Application Development) course. I built a web-based parking management system using Flask and SQLAlchemy. The system allows users to book parking spots and administrators to manage parking lots.

## Features

### For Users:
- View available parking lots
- Book parking spots
- View booking history
- Release parking spots when done

### For Administrators:
- Create and manage parking lots
- View system statistics
- Monitor parking spot usage
- Generate revenue reports

## Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 + Custom CSS
- **Authentication**: Flask-Login
- **Icons**: Font Awesome

## Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd parking-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and go to `http://localhost:5000`

## Default Login Credentials
- **Admin**: username: `admin`, password: `admin`
- **Users**: Register a new account to get started

## Project Structure
```
├── app.py              # Main application file
├── models/             # Database models
│   ├── __init__.py     # Package initialization
│   └── models.py       # Database models
├── controllers/        # Application logic
│   ├── __init__.py     # Package initialization
│   ├── routes.py       # Route handlers
│   ├── api.py          # API endpoints
│   ├── extensions.py   # Flask extensions
│   └── config.py       # Configuration settings
├── static/             # CSS and static files
├── templates/          # HTML templates
├── instance/           # Database files
└── requirements.txt    # Python dependencies
```

## Database Schema
- **Users**: Store user accounts and roles
- **ParkingLots**: Store parking lot information
- **ParkingSpots**: Individual parking spots within lots
- **Reservations**: Track parking bookings

## API Endpoints
The system includes REST API endpoints for future mobile app integration:
- `GET /parking-lots` - Get all parking lots
- `GET /parking-lot/<id>/spots` - Get spots in a lot
- `POST /reserve` - Make a reservation
- `GET /user/<id>/reservations` - Get user reservations

## Future Improvements
- Add payment processing
- Implement real-time spot availability
- Add email notifications
- Create mobile app
- Add user ratings and reviews

## Challenges Faced
- Learning Flask and SQLAlchemy from scratch
- Implementing proper authentication and authorization
- Making the UI responsive and user-friendly
- Handling database relationships correctly

## What I Learned
- Web development with Flask
- Database design and ORM usage
- User authentication and session management
- Frontend development with Bootstrap
- API design and implementation
- Basic project organization and structure

## Screenshots
[Add screenshots here when you have them]

## License
This project is created for educational purposes as part of the MAD course.

---
**Created by**: Arjun Kumar Singh  
**Student ID**: 23f2003539@ds.study.iitm.ac.in
**Course**: MAD - Mobile Application Development  
**Date**: July 2025