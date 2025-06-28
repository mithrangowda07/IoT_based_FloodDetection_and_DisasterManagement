"""
Flood Monitoring System - Desktop Application
============================================

This application monitors river levels and provides flood risk analysis.
All sensitive credentials (Twilio API keys) are loaded from environment variables
and are NOT hardcoded in this source code.

SECURITY NOTICE: No API keys, tokens, or secrets are stored in this file.
All credentials must be provided via environment variables in a config.env file.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import serial
import time
from datetime import datetime
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')


class FloodMonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flood Monitoring System")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Set theme colors
        self.bg_color = "#f0f2f5"
        self.card_color = "#ffffff"
        self.primary_color = "#4e73df"
        self.danger_color = "#e74a3b"
        self.warning_color = "#f6c23e"
        self.success_color = "#1cc88a"
        self.text_color = "#5a5c69"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Twilio Configuration - Load from environment variables only
        # No hardcoded secrets in this application
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')
        emergency_numbers_str = os.getenv('EMERGENCY_NUMBERS', '')
        self.emergency_numbers = [num.strip() for num in emergency_numbers_str.split(',') if num.strip()]
        
        # Initialize Twilio client only if all required environment variables are present
        self.twilio_client = None
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            print("Twilio configuration incomplete - SMS alerts will be disabled")
            print("Please create a config.env file with your Twilio credentials")
            messagebox.showinfo("SMS Configuration", 
                              "SMS alerts are not configured.\n"
                              "To enable SMS alerts, create a config.env file with:\n"
                              "- TWILIO_ACCOUNT_SID\n"
                              "- TWILIO_AUTH_TOKEN\n"
                              "- TWILIO_FROM_NUMBER\n"
                              "- EMERGENCY_NUMBERS")
        else:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                print("Twilio configuration loaded successfully from environment variables")
            except Exception as e:
                print(f"Error initializing Twilio client: {e}")
                messagebox.showwarning("Twilio Error", 
                                     f"Failed to initialize Twilio client: {e}\n"
                                     "SMS alerts will be disabled.")
                self.twilio_client = None
        
        # Alert tracking
        self.last_alert_time = None
        self.ALERT_COOLDOWN = 1800  # 30 minutes in seconds
        
        # Serial connection
        self.serial_connection = None
        self.rainfall_intensity = 0.0
        
        # Data variables
        self.sensor_height = 0.0  # Raw sensor reading
        self.river_height = 0.0   # Actual river height
        self.flow_rate = 0.0
        
        # Constants
        self.SENSOR_MAX_HEIGHT = 20.0  # Distance from sensor to river bed in cm
        self.NORMAL_RIVER_HEIGHT = 10.0  # Normal river height in cm
        self.NORMAL_FLOW_RATE = 1.0     # Normal flow rate in L/min
        self.AREA_KM2 = 1.0  # Area in square kilometers
        self.DAM_CAPACITY = 50000.0  # Dam capacity in cubic meters

        # GUI components
        self.setup_ui()

        # Attempt to establish a serial connection
        self.connect_to_arduino()

        # Update the GUI dynamically
        self.update_gui()

    def send_alert(self, message):
        """Send SMS alert using Twilio credentials loaded from environment variables"""
        # Only send alerts if Twilio client is properly initialized with environment variables
        if not self.twilio_client:
            print("SMS alerts disabled - Twilio client not initialized")
            return

        # Check if enough time has passed since last alert
        current_time = time.time()
        if (self.last_alert_time and 
            current_time - self.last_alert_time < self.ALERT_COOLDOWN):
            return  # Don't send alert if within cooldown period

        try:
            # Send SMS to all configured emergency numbers from environment variables
            for number in self.emergency_numbers:
                self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_from_number,  # From environment variable
                    to=number
                )
            print(f"Alert sent successfully via Twilio: {message}")
            self.last_alert_time = current_time
        except Exception as e:
            print(f"Error sending SMS alert via Twilio: {e}")

    def setup_ui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.card_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=self.primary_color, background=self.bg_color)
        style.configure('Card.TFrame', background=self.card_color, relief=tk.RAISED, borderwidth=2)
        style.configure('CardHeader.TLabel', font=('Segoe UI', 12, 'bold'), foreground=self.primary_color, background=self.card_color)
        style.configure('Data.TLabel', font=('Segoe UI', 11), background=self.card_color)
        style.configure('Alert.TLabel', foreground=self.danger_color, font=('Segoe UI', 11, 'bold'), background=self.card_color)
        style.configure('Warning.TLabel', foreground=self.warning_color, font=('Segoe UI', 11, 'bold'), background=self.card_color)
        style.configure('Normal.TLabel', foreground=self.success_color, font=('Segoe UI', 11), background=self.card_color)
        style.configure('TButton', font=('Segoe UI', 10), background=self.primary_color, foreground='white')
        style.map('TButton', background=[('active', self.primary_color)], foreground=[('active', 'white')])
        style.configure('TEntry', font=('Segoe UI', 10), padding=5)
        
        # Main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(self.main_container)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="Flood Monitoring System", style='Title.TLabel')
        title_label.pack()
        
        # Dashboard cards
        self.create_sensor_card()
        self.create_input_card()
        self.create_analysis_card()
        self.create_status_bar()

    def create_sensor_card(self):
        """Create the river status card"""
        card = ttk.Frame(self.main_container, style='Card.TFrame', padding="15")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Card header
        header = ttk.Frame(card)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="River Status", style='CardHeader.TLabel').pack(side=tk.LEFT)
        
        # Data rows
        data_frame = ttk.Frame(card)
        data_frame.pack(fill=tk.X)
        
        # River Height
        row1 = ttk.Frame(data_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="River Height:", style='Data.TLabel').pack(side=tk.LEFT)
        self.height_label = ttk.Label(row1, text="N/A cm", style='Data.TLabel')
        self.height_label.pack(side=tk.RIGHT)
        
        # Flow Rate
        row2 = ttk.Frame(data_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="Water Flow Rate:", style='Data.TLabel').pack(side=tk.LEFT)
        self.flow_rate_label = ttk.Label(row2, text="N/A L/min", style='Data.TLabel')
        self.flow_rate_label.pack(side=tk.RIGHT)
        
        # Status
        row3 = ttk.Frame(data_frame)
        row3.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(row3, text="Status:", style='Data.TLabel').pack(side=tk.LEFT)
        self.status_label = ttk.Label(row3, text="N/A", style='Normal.TLabel')
        self.status_label.pack(side=tk.RIGHT)

    def create_input_card(self):
        """Create the input parameters card"""
        card = ttk.Frame(self.main_container, style='Card.TFrame', padding="15")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Card header
        header = ttk.Frame(card)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Calculation Parameters", style='CardHeader.TLabel').pack(side=tk.LEFT)
        
        # Input fields
        input_frame = ttk.Frame(card)
        input_frame.pack(fill=tk.X)
        
        # Rainfall Intensity
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="Rainfall Intensity (mm/h):", style='Data.TLabel').pack(side=tk.LEFT)
        self.intensity_entry = ttk.Entry(row1, font=('Segoe UI', 10), width=10)
        self.intensity_entry.pack(side=tk.RIGHT, padx=5)
        self.intensity_entry.insert(0, "0")
        
        # Duration
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="Duration (hrs):", style='Data.TLabel').pack(side=tk.LEFT)
        self.duration_entry = ttk.Entry(row2, font=('Segoe UI', 10), width=10)
        self.duration_entry.pack(side=tk.RIGHT, padx=5)
        self.duration_entry.insert(0, "1")
        
        # Calculate button
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self.calculate_button = ttk.Button(btn_frame, text="Calculate Risk", command=self.calculate, style='TButton')
        self.calculate_button.pack(pady=5, ipadx=10, ipady=5)

    def create_analysis_card(self):
        """Create the flood risk analysis card"""
        card = ttk.Frame(self.main_container, style='Card.TFrame', padding="15")
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Card header
        header = ttk.Frame(card)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Flood Risk Analysis", style='CardHeader.TLabel').pack(side=tk.LEFT)
        
        # Analysis results
        analysis_frame = ttk.Frame(card)
        analysis_frame.pack(fill=tk.X)
        
        # Risk Level
        row1 = ttk.Frame(analysis_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="Risk Level:", style='Data.TLabel').pack(side=tk.LEFT)
        self.risk_label = ttk.Label(row1, text="N/A", style='Normal.TLabel')
        self.risk_label.pack(side=tk.RIGHT)
        
        # Dam Status
        row2 = ttk.Frame(analysis_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="Dam Status:", style='Data.TLabel').pack(side=tk.LEFT)
        self.capacity_label = ttk.Label(row2, text="N/A", style='Data.TLabel')
        self.capacity_label.pack(side=tk.RIGHT)
        
        # Time to Fill
        row3 = ttk.Frame(analysis_frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Label(row3, text="Time to Fill:", style='Data.TLabel').pack(side=tk.LEFT)
        self.time_to_fill_label = ttk.Label(row3, text="N/A", style='Normal.TLabel')
        self.time_to_fill_label.pack(side=tk.RIGHT)

    def create_status_bar(self):
        """Create the status bar at the bottom"""
        status_bar = ttk.Frame(self.main_container, style='Card.TFrame', padding="10")
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Connection status
        conn_frame = ttk.Frame(status_bar)
        conn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(conn_frame, text="Connection:", style='Data.TLabel').pack(side=tk.LEFT)
        self.connection_label = ttk.Label(conn_frame, text="Not Connected", style='Alert.TLabel')
        self.connection_label.pack(side=tk.LEFT, padx=5)
        
        # Timestamp
        timestamp_frame = ttk.Frame(status_bar)
        timestamp_frame.pack(side=tk.RIGHT)
        self.timestamp_label = ttk.Label(timestamp_frame, text="Last Updated: Never", style='Data.TLabel')
        self.timestamp_label.pack(side=tk.RIGHT)

    def connect_to_arduino(self):
        try:
            self.serial_connection = serial.Serial(port="COM5", baudrate=115200, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.connection_label.config(text="Connected to COM5", style='Normal.TLabel')
            print("Connected to Arduino on COM5")
            
            # Flush any leftover data
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
        except serial.SerialException as e:
            self.connection_label.config(text=f"Connection Error: {str(e)}", style='Alert.TLabel')
            messagebox.showerror("Connection Error", f"Could not connect to Arduino: {e}")

    def check_flood_status(self):
        """Determine flood status based on river height and flow rate"""
        if self.river_height > self.NORMAL_RIVER_HEIGHT:
            if self.flow_rate > self.NORMAL_FLOW_RATE * 2:  # High flow rate
                status = "SEVERE FLOOD ALERT"
                style = 'Alert.TLabel'
                # Send SMS alert for severe flood
                self.send_alert(
                    f"SEVERE FLOOD ALERT!\n"
                    f"River Height: {self.river_height:.1f}cm\n"
                    f"Flow Rate: {self.flow_rate:.1f}L/min\n"
                    f"Location: River Monitoring Station"
                )
            else:
                status = "FLOOD WARNING"
                style = 'Warning.TLabel'
                # Send SMS alert for flood warning
                self.send_alert(
                    f"FLOOD WARNING!\n"
                    f"River Height: {self.river_height:.1f}cm\n"
                    f"Flow Rate: {self.flow_rate:.1f}L/min\n"
                    f"Location: River Monitoring Station"
                )
        elif self.flow_rate > self.NORMAL_FLOW_RATE * 2:
            status = "HIGH FLOW WARNING"
            style = 'Warning.TLabel'
        else:
            status = "Normal Conditions"
            style = 'Normal.TLabel'
        
        return status, style

    def update_gui(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8").strip()
                    print(f"Raw data received: {line}")  # Debug print
                    
                    if line:
                        parts = line.split(",")
                        if len(parts) == 2:
                            try:
                                # Parse sensor height and flow rate
                                self.sensor_height = float(parts[0])
                                self.flow_rate = float(parts[1])
                                
                                # Calculate actual river height
                                self.river_height = self.SENSOR_MAX_HEIGHT - self.sensor_height
                                
                                # Update labels
                                self.height_label.config(
                                    text=f"{self.river_height:.1f} cm"
                                )
                                self.flow_rate_label.config(
                                    text=f"{self.flow_rate:.2f} L/min"
                                )
                                
                                # Update flood status
                                status, style = self.check_flood_status()
                                self.status_label.config(
                                    text=status,
                                    style=style
                                )
                                
                                # Update timestamp
                                self.timestamp_label.config(
                                    text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
                                )
                                
                                print(f"Processed - River Height: {self.river_height} cm, "
                                      f"Flow Rate: {self.flow_rate} L/min")
                                
                                # Only auto-calculate if we have valid input
                                try:
                                    intensity = float(self.intensity_entry.get())
                                    duration = float(self.duration_entry.get())
                                    if intensity >= 0 and duration > 0:
                                        self.calculate(show_errors=False)
                                except ValueError:
                                    pass
                                    
                            except ValueError as e:
                                print(f"Error parsing values: {e}")
                        else:
                            print(f"Unexpected data format. Expected 2 values, got: {len(parts)}")
                    
            except Exception as e:
                print(f"Error reading serial: {e}")
                try:
                    self.serial_connection.close()
                    time.sleep(1)
                    self.connect_to_arduino()
                except:
                    pass

        # Call this method again after 100ms
        self.root.after(100, self.update_gui)

    def calculate_time_to_fill(self, remaining_capacity, intensity, flow_rate):
        """Calculate time until area is filled based on flow rate and rainfall"""
        # Convert flow rate from L/min to m³/hour
        flow_volume_per_hour = flow_rate * 60 / 1000  # L/min -> m³/hour
        
        # Calculate rainfall volume per hour
        rainfall_volume_per_hour = (intensity / 1000) * self.AREA_KM2 * 1e6  # m³/hour
        
        # Total inflow per hour
        total_inflow_per_hour = flow_volume_per_hour + rainfall_volume_per_hour
        
        if total_inflow_per_hour <= 0:
            return float('inf')
            
        # Calculate time to fill in hours
        time_to_fill = remaining_capacity / total_inflow_per_hour
        
        return time_to_fill

    def format_time(self, hours):
        """Format hours into a readable time string"""
        if hours == float('inf'):
            return "N/A (no inflow)"
            
        if hours < 0:
            return "Area Already Filled"
            
        days = int(hours // 24)
        remaining_hours = int(hours % 24)
        minutes = int((hours * 60) % 60)
        
        if days > 0:
            return f"{days}d {remaining_hours}h {minutes}m"
        elif remaining_hours > 0:
            return f"{remaining_hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def calculate(self, show_errors=True):
        try:
            duration = float(self.duration_entry.get())
            intensity = float(self.intensity_entry.get())
            
            if duration <= 0 or intensity < 0:
                raise ValueError("Duration must be positive and intensity must be non-negative")

            # Calculate incoming water volume
            incoming_volume = (intensity / 1000) * self.AREA_KM2 * 1e6 * duration
            remaining_capacity = self.DAM_CAPACITY - incoming_volume

            # Calculate time to fill
            time_to_fill = self.calculate_time_to_fill(remaining_capacity, intensity, self.flow_rate)
            time_str = self.format_time(time_to_fill)

            # Update risk analysis based on both sensor data and calculations
            if remaining_capacity < 0:
                risk_text = "CRITICAL - Dam Capacity Exceeded"
                risk_style = 'Alert.TLabel'
                capacity_text = f"Excess Volume: {abs(remaining_capacity):.2f} m³"
                time_text = f"Time to Fill: {time_str}"
            else:
                if self.river_height > self.NORMAL_RIVER_HEIGHT:
                    if remaining_capacity < self.DAM_CAPACITY * 0.2:
                        risk_text = "HIGH RISK - Flood Conditions with Low Capacity"
                        risk_style = 'Alert.TLabel'
                    else:
                        risk_text = "MODERATE RISK - Flood Conditions"
                        risk_style = 'Warning.TLabel'
                else:
                    if remaining_capacity < self.DAM_CAPACITY * 0.2:
                        risk_text = "CAUTION - Low Dam Capacity"
                        risk_style = 'Warning.TLabel'
                    else:
                        risk_text = "LOW RISK - Normal Conditions"
                        risk_style = 'Normal.TLabel'
                capacity_text = f"Remaining Capacity: {remaining_capacity:.2f} m³"
                
                if time_to_fill < 24:  # Less than 24 hours to fill
                    time_text = f"Time to Fill: {time_str} (URGENT!)"
                    self.time_to_fill_label.config(style='Alert.TLabel')
                elif time_to_fill < 72:  # Less than 3 days to fill
                    time_text = f"Time to Fill: {time_str} (WARNING)"
                    self.time_to_fill_label.config(style='Warning.TLabel')
                else:
                    time_text = f"Time to Fill: {time_str}"
                    self.time_to_fill_label.config(style='Normal.TLabel')
            
            self.risk_label.config(text=risk_text, style=risk_style)
            self.capacity_label.config(text=capacity_text)
            self.time_to_fill_label.config(text=time_text)

        except ValueError as e:
            if show_errors:
                messagebox.showerror("Input Error", "Please enter valid numbers for duration and intensity")
        except Exception as e:
            if show_errors:
                messagebox.showerror("Calculation Error", f"Error: {e}")

    def on_closing(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FloodMonitoringApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()