# Part B: Web-based Disaster Management System

## Overview
A comprehensive disaster management system consisting of two components:
1. **ESP32 Captive Portal**: A standalone web server running on ESP32 for emergency incident reporting
2. **Flask Web Application**: A full-featured web application with user authentication, incident management, and admin panel

## Features

### ESP32 Captive Portal
- **Standalone Operation**: Works without internet connection
- **Emergency Reporting**: Quick incident reporting interface
- **WiFi Access Point**: Creates its own network for connectivity
- **Real-time Updates**: Instant incident submission and status tracking

### Flask Web Application
- **User Authentication**: Secure login/registration system
- **Incident Reporting**: Detailed disaster incident submissions
- **Admin Panel**: Complete incident management interface
- **Database Storage**: SQLite database for persistent data
- **Location Tracking**: GPS coordinates for incident locations
- **Status Management**: Track and update incident resolution status

## System Architecture

```
ESP32 Captive Portal (Emergency Mode)
├── WiFi Access Point
├── Web Server (Port 80)
├── Incident Reporting Interface
└── Local Data Storage

Flask Web Application (Full System)
├── User Authentication
├── Incident Management
├── Admin Dashboard
├── SQLite Database
└── Web Interface
```

## Prerequisites
- ESP32 development board
- Python 3.7+ (for Flask application)
- Web browser
- WiFi-capable device (for ESP32 portal)

## Installation & Setup

### ESP32 Captive Portal Setup

#### 1. Hardware Requirements
- ESP32 development board
- USB cable for programming

#### 2. Software Setup
1. Install Arduino IDE with ESP32 board support
2. Open `esp32_captive_portal.ino` in Arduino IDE
3. Select your ESP32 board and port
4. Upload the code to ESP32

#### 3. Configuration
Default WiFi settings (modify in code if needed):
- **SSID**: DisasterManagement
- **Password**: 123456789
- **IP Address**: 192.168.4.1

### Flask Web Application Setup

#### 1. Install Dependencies
```bash
cd part_B
pip install flask flask-sqlalchemy werkzeug
```

#### 2. Database Setup
The application automatically creates the database on first run:
```bash
python app.py
```

#### 3. Default Admin Credentials
- **Username**: admin
- **Password**: admin123

**Important**: Change these credentials in production!

## Usage

### ESP32 Captive Portal (Emergency Mode)

#### 1. Power Up ESP32
- Connect ESP32 to power
- Wait for WiFi network to appear

#### 2. Connect to Network
- Connect your device to "DisasterManagement" WiFi network
- Password: 123456789

#### 3. Access Portal
- Open web browser
- Navigate to: http://192.168.4.1
- Or wait for captive portal to appear automatically

#### 4. Report Incident
- Fill in incident details:
  - Your name
  - Number of people affected
  - Location/coordinates
- Submit the report

### Flask Web Application (Full System)

#### 1. Start the Application
```bash
python app.py
```

#### 2. Access the Application
- Open browser and go to: http://localhost:5000

#### 3. User Registration/Login
- Register a new account or login with existing credentials
- Admin login available at: http://localhost:5000/admin_login

#### 4. Report Incidents
- Navigate to user dashboard
- Fill in detailed incident information:
  - Personal details
  - Contact information
  - GPS coordinates (format: latitude,longitude)
  - Incident description
- Submit report

#### 5. Admin Management
- Login as admin
- View all submitted incidents
- Mark incidents as solved
- Delete resolved incidents
- Track incident statistics

## File Structure

```
part_B/
├── app.py                      # Flask web application
├── main.py                     # ESP32 web server code
├── boot.py                     # ESP32 boot configuration
├── disaster_management.db      # SQLite database
├── esp32_captive_portal.ino    # ESP32 captive portal code
├── esp32.ino                   # ESP32 basic setup
├── README.md                   # This file
└── templates/                  # HTML templates
    ├── home.html              # Home page
    ├── login.html             # User login
    ├── register.html          # User registration
    ├── user.html              # User dashboard
    ├── admin_login.html       # Admin login
    ├── admin.html             # Admin dashboard
    └── submission_success.html # Success page
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: User email address
- `password_hash`: Encrypted password

### Reports Table
- `id`: Primary key
- `name`: Reporter's name
- `phone`: Contact number
- `coordinates`: GPS coordinates
- `description`: Incident details
- `timestamp`: Submission time
- `solved`: Resolution status
- `user_id`: Foreign key to Users

## Configuration

### ESP32 Settings
Modify these constants in `esp32_captive_portal.ino`:
```cpp
const char* ssid = "DisasterManagement";
const char* password = "123456789";
const int port = 80;
```

### Flask Settings
Modify in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
```

## Security Features

### ESP32 Portal
- WiFi password protection
- Input validation
- Local data storage only

### Flask Application
- Password hashing with Werkzeug
- Session management
- Admin authentication
- SQL injection protection
- Input validation and sanitization

## Troubleshooting

### ESP32 Issues
1. **WiFi not appearing**: Check power supply and reset ESP32
2. **Portal not loading**: Clear browser cache and try again
3. **Connection drops**: Check WiFi signal strength
4. **Upload errors**: Verify board selection and port

### Flask Application Issues
1. **Database errors**: Check file permissions and disk space
2. **Login problems**: Verify admin credentials
3. **Port conflicts**: Change port in app.py
4. **Import errors**: Install missing dependencies

### General Issues
1. **Coordinates validation**: Use format "latitude,longitude" (e.g., "12.922835,77.50111")
2. **Session problems**: Clear browser cookies
3. **Performance issues**: Check database size and optimize queries

## Emergency Procedures

### When Internet is Available
- Use Flask web application for full functionality
- Access admin panel for incident management
- Database backup and recovery

### When Internet is Down
- Use ESP32 captive portal for emergency reporting
- Local data storage on ESP32
- Manual data transfer when connectivity restored

## API Endpoints (Flask)

- `GET /`: Home page
- `GET/POST /register`: User registration
- `GET/POST /login`: User login
- `GET/POST /admin_login`: Admin login
- `GET/POST /user`: User dashboard and incident reporting
- `GET /admin`: Admin dashboard
- `POST /admin_action`: Admin actions (solve/delete incidents)
- `GET /submission_success`: Success page
- `GET /logout`: Logout

## Contributing
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on both ESP32 and Flask components
4. Submit a pull request

## License
This project is part of the Civil Engineering IoT-based Flood Detection and Disaster Management system.

## Support
For issues and questions:
1. Check the troubleshooting section
2. Verify hardware connections
3. Review ESP32 documentation
4. Check Flask and SQLAlchemy documentation
5. Open an issue in the repository 