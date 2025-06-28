# Civil EL - Emergency Response and Flood Monitoring System

A comprehensive disaster management and flood monitoring system built with Python, Flask, ESP32 microcontrollers, and IoT sensors. This project consists of two main components: a flood monitoring system with real-time alerts and a disaster communication portal.

## 🚨 Project Overview

This system provides:
- **Real-time flood monitoring** with ultrasonic sensors and flow rate measurement
- **SMS alerts** via Twilio for emergency situations
- **Disaster communication portal** for affected individuals to report their status
- **Admin dashboard** for emergency response coordination
- **ESP32-based captive portal** for offline communication during disasters

## 📁 Project Structure

```
Civil EL/
├── part_A/                          # Flood Monitoring System
│   ├── app.py                       # Main flood monitoring application
│   ├── config.env                   # Environment variables (not in git)
│   ├── config.env.example           # Example configuration file
│   ├── esp32_code/
│   │   └── flood_monitoring.ino     # ESP32 code for sensors
│   └── requirements.txt             # Python dependencies
├── part_B/                          # Disaster Communication System
│   ├── app.py                       # Flask web application
│   ├── boot.py                      # ESP32 boot configuration
│   ├── main.py                      # ESP32 main application
│   ├── esp32_captive_portal.ino     # ESP32 captive portal code
│   ├── esp32.ino                    # ESP32 main code
│   ├── disaster_management.db       # SQLite database
│   ├── templates/                   # HTML templates
│   │   ├── admin.html
│   │   ├── admin_login.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── submission_success.html
│   │   └── user.html
│   └── requirements.txt             # Python dependencies
├── requirements.txt                 # Main project dependencies
├── .gitignore                       # Git ignore rules
└── sensor_test/                     # Sensor testing utilities
```

## 🔧 Hardware Requirements

### Part A - Flood Monitoring System
- **ESP32 Development Board**
- **HC-SR04 Ultrasonic Sensor** (for water level measurement)
- **YF-S201 Water Flow Sensor** (for flow rate measurement)
- **Connecting wires and breadboard**
- **Power supply for ESP32**

### Part B - Disaster Communication System
- **ESP32 Development Board** (for captive portal)
- **Computer/Server** (for Flask web application)

## 🛠️ Software Requirements

### Part A - Flood Monitoring System
```bash
pip install -r part_A/requirements.txt
```

Required packages:
- `flask==3.0.0`
- `pyserial==3.5`
- `twilio==8.10.0`
- `python-dotenv==1.0.0`

### Part B - Disaster Communication System
```bash
pip install -r part_B/requirements.txt
```

Required packages:
- `flask==3.0.0`
- `requests==2.31.0`

## 🚀 Installation and Setup

### Part A: Flood Monitoring System

1. **Hardware Setup:**
   - Connect the ultrasonic sensor to ESP32:
     - Trig pin → GPIO 5
     - Echo pin → GPIO 18
     - VCC → 5V
     - GND → GND
   - Connect the water flow sensor to ESP32:
     - Signal pin → GPIO 27
     - VCC → 5V
     - GND → GND

2. **ESP32 Code Upload:**
   - Open `part_A/esp32_code/flood_monitoring.ino` in Arduino IDE
   - Install ESP32 board support package
   - Upload the code to your ESP32

3. **Python Application Setup:**
   ```bash
   cd part_A
   pip install -r requirements.txt
   ```

4. **Twilio Configuration:**
   - Sign up for a Twilio account at [twilio.com](https://www.twilio.com)
   - Copy the example configuration file:
     ```bash
     cp config.env.example config.env
     ```
   - Edit `config.env` with your Twilio credentials:
     ```env
     TWILIO_ACCOUNT_SID=your_account_sid_here
     TWILIO_AUTH_TOKEN=your_auth_token_here
     TWILIO_FROM_NUMBER=your_twilio_phone_number_here
     EMERGENCY_NUMBERS=+1234567890,+0987654321
     ```
   - **Important:** Never commit the `config.env` file to version control!

5. **Run the Application:**
   ```bash
   python app.py
   ```

### Part B: Disaster Communication System

1. **Flask Application Setup:**
   ```bash
   cd part_B
   pip install -r requirements.txt
   python app.py
   ```

2. **ESP32 Captive Portal Setup:**
   - Upload `esp32_captive_portal.ino` to your ESP32
   - The ESP32 will create a WiFi hotspot named "DisasterManagement"
   - Password: "123456789"

3. **Database Setup:**
   - The SQLite database will be automatically created on first run
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## 🔐 Security Features

- **Environment variables** for sensitive configuration
- **Password hashing** using Werkzeug security
- **Session management** for user authentication
- **Admin access control** with separate login system
- **Input validation** for coordinates and user data
- **SQL injection protection** through SQLAlchemy ORM
- **Git ignore rules** to prevent committing sensitive files

## 📊 Features

### Flood Monitoring System (Part A)
- **Real-time water level monitoring** using ultrasonic sensors
- **Flow rate measurement** using water flow sensors
- **Flood risk calculation** based on rainfall intensity and duration
- **SMS alerts** for emergency situations via Twilio
- **Graphical user interface** with real-time data visualization
- **Alert cooldown system** to prevent spam notifications

### Disaster Communication System (Part B)
- **User registration and authentication**
- **Emergency report submission** with location coordinates
- **Admin dashboard** for managing emergency reports
- **ESP32 captive portal** for offline communication
- **Google Maps integration** for location visualization
- **Report status tracking** (solved/unsolved)

## 📱 Usage

### Flood Monitoring System
1. Launch the application: `python app.py`
2. Connect to ESP32 via serial port
3. Monitor real-time water level and flow rate
4. Enter rainfall intensity and duration for risk calculation
5. Receive SMS alerts for flood warnings

### Disaster Communication System
1. **For Users:**
   - Register an account or login
   - Submit emergency reports with location and details
   - Track report status

2. **For Admins:**
   - Login with admin credentials
   - View all emergency reports
   - Mark reports as solved
   - Coordinate emergency response

3. **ESP32 Captive Portal:**
   - Connect to "DisasterManagement" WiFi network
   - Access the portal at `192.168.4.1`
   - Submit reports or access admin panel

## 🚨 Emergency Response Workflow

1. **Detection:** Flood monitoring system detects dangerous water levels
2. **Alert:** SMS alerts sent to emergency contacts
3. **Communication:** Affected individuals use the communication portal
4. **Coordination:** Emergency responders use admin dashboard
5. **Response:** Reports tracked and managed through the system

## 🔧 Configuration

### Alert Thresholds
Modify these values in `part_A/app.py`:
```python
self.NORMAL_RIVER_HEIGHT = 10.0  # Normal river height in cm
self.SENSOR_MAX_HEIGHT = 20.0    # Distance from sensor to river bed
self.ALERT_COOLDOWN = 1800       # Alert cooldown in seconds
```

### Network Configuration
Modify WiFi settings in `part_B/esp32_captive_portal.ino`:
```cpp
const char* ssid = "DisasterManagement";
const char* password = "123456789";
```

### Environment Variables
The system uses environment variables for sensitive configuration. Create a `config.env` file in the `part_A` directory:
```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number_here
EMERGENCY_NUMBERS=+1234567890,+0987654321
```

## 🐛 Troubleshooting

### Common Issues

1. **Serial Connection Failed:**
   - Check COM port settings
   - Ensure ESP32 is properly connected
   - Verify baud rate (115200)

2. **SMS Alerts Not Working:**
   - Verify Twilio credentials in `config.env`
   - Check emergency phone numbers
   - Ensure sufficient Twilio credits
   - Make sure `config.env` file exists and is properly formatted

3. **Database Errors:**
   - Delete `disaster_management.db` and restart
   - Check file permissions

4. **ESP32 WiFi Issues:**
   - Reset ESP32
   - Check WiFi credentials
   - Ensure proper power supply

5. **Environment Variables Not Loading:**
   - Ensure `config.env` file exists in the correct directory
   - Check file format (no spaces around `=` sign)
   - Verify `python-dotenv` is installed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Important:** Never commit sensitive files like `config.env` or database files.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Civil Engineering Team
- Emergency Response Development Team

## 🙏 Acknowledgments

- Twilio for SMS services
- Arduino community for ESP32 support
- Flask framework for web development
- Emergency response organizations for feedback

## 📞 Support

For technical support or emergency response coordination, please contact the development team or local emergency services.

---

**⚠️ Important:** 
- This system is designed for emergency response and should be used in conjunction with official emergency services. Always verify alerts and coordinate with local authorities during actual emergencies.
- **Security Note:** Never commit sensitive configuration files to version control. Always use environment variables for API keys and credentials. 