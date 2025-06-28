# Part A: Flood Monitoring Desktop Application

## Overview
A Python-based desktop application for real-time flood monitoring and risk assessment. This application connects to ESP32 sensors to monitor river levels and water flow rates, providing instant flood risk analysis and SMS alerts.

## Features
- **Real-time Monitoring**: Live river height and flow rate monitoring via ESP32 sensors
- **Flood Risk Analysis**: Advanced risk assessment based on sensor data and rainfall parameters
- **SMS Alerts**: Automated emergency notifications via Twilio when flood conditions are detected
- **Modern UI**: Clean, responsive interface with real-time data visualization
- **Dam Capacity Monitoring**: Tracks remaining dam capacity and time to fill calculations
- **Serial Communication**: Direct connection to ESP32 for sensor data acquisition

## Prerequisites
- Python 3.7 or higher
- ESP32 microcontroller with flood monitoring sensors
- Twilio account (for SMS alerts - optional)
- Serial connection capability

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Civil EL/part_A"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example configuration file and add your credentials:
```bash
cp config.env.example config.env
```

Edit `config.env` with your Twilio credentials (optional):
```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number_here
EMERGENCY_NUMBERS=+1234567890,+0987654321
```

### 4. ESP32 Setup
1. Upload the `esp32_code/flood_monitoring.ino` sketch to your ESP32
2. Connect the ESP32 to your computer via USB
3. Note the COM port (default: COM5)

## Usage

### Starting the Application
```bash
python app.py
```

### Interface Components

#### River Status Card
- **River Height**: Real-time water level in centimeters
- **Water Flow Rate**: Current flow rate in liters per minute
- **Status**: Current flood status (Normal, Warning, Severe Alert)

#### Calculation Parameters
- **Rainfall Intensity**: Input rainfall intensity in mm/hour
- **Duration**: Duration of rainfall in hours
- **Calculate Risk**: Button to perform risk analysis

#### Flood Risk Analysis
- **Risk Level**: Overall flood risk assessment
- **Dam Status**: Remaining dam capacity
- **Time to Fill**: Estimated time until dam reaches capacity

#### Status Bar
- **Connection Status**: ESP32 connection status
- **Last Updated**: Timestamp of last sensor reading

### Alert System
The application automatically sends SMS alerts when:
- River height exceeds normal levels
- Flow rate indicates flood conditions
- Dam capacity is critically low

Alerts are sent with a 30-minute cooldown to prevent spam.

## Configuration

### Sensor Parameters
Edit these constants in `app.py` to match your setup:
```python
self.SENSOR_MAX_HEIGHT = 20.0  # Distance from sensor to river bed (cm)
self.NORMAL_RIVER_HEIGHT = 10.0  # Normal river height (cm)
self.NORMAL_FLOW_RATE = 1.0     # Normal flow rate (L/min)
self.AREA_KM2 = 1.0  # Watershed area (km²)
self.DAM_CAPACITY = 50000.0  # Dam capacity (m³)
```

### Serial Connection
Default settings:
- Port: COM5
- Baud Rate: 115200
- Timeout: 1 second

To change the port, modify the `connect_to_arduino()` method in `app.py`.

## Troubleshooting

### Connection Issues
1. **ESP32 not detected**: Check USB connection and drivers
2. **Wrong COM port**: Update port in `connect_to_arduino()` method
3. **Serial timeout**: Increase timeout value or check ESP32 code

### SMS Alert Issues
1. **Twilio not configured**: Check `config.env` file
2. **Invalid phone numbers**: Ensure emergency numbers include country codes
3. **API errors**: Verify Twilio credentials and account status

### Data Issues
1. **Invalid sensor readings**: Check ESP32 sensor connections
2. **Calculation errors**: Verify input parameters are positive numbers
3. **UI not updating**: Check serial connection status

## Security
- All credentials are loaded from environment variables
- No hardcoded secrets in source code
- `config.env` file is gitignored
- See `SECURITY.md` for detailed security information

## File Structure
```
part_A/
├── app.py                 # Main application file
├── config.env.example     # Environment variables template
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── SECURITY.md           # Security documentation
└── esp32_code/
    └── flood_monitoring.ino  # ESP32 sensor code
```

## Dependencies
- `tkinter`: GUI framework
- `pyserial`: Serial communication
- `twilio`: SMS alert service
- `python-dotenv`: Environment variable management

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is part of the Civil Engineering IoT-based Flood Detection and Disaster Management system.

## Support
For issues and questions:
1. Check the troubleshooting section
2. Review the ESP32 code documentation
3. Check Twilio documentation for SMS setup
4. Open an issue in the repository 