import network
import socket
import json
from machine import Pin
import time

# Initialize storage
reports = []
admin_password = "admin123"

# WiFi Access Point Configuration
SSID = "DisasterManagement"
PASSWORD = "123456789"

def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)
    while not ap.active():
        pass
    print('AP Mode Active')
    print('Network config:', ap.ifconfig())
    return ap

def parse_request(request):
    # Parse HTTP request to get method and path
    request = request.decode('utf-8')
    request_line = request.split('\r\n')[0]
    method, path, _ = request_line.split(' ')
    return method, path

def create_response(status="200 OK", content_type="text/html", content=""):
    response = f"HTTP/1.1 {status}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Connection: close\r\n\r\n"
    response += content
    return response

def handle_post_data(request):
    # Simple POST data parser
    data = {}
    if '\r\n\r\n' in request:
        body = request.split('\r\n\r\n')[1]
        pairs = body.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=')
                data[key] = value
    return data

def render_template(name, **kwargs):
    if name == 'home.html':
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Disaster Management</title></head>
        <body>
            <h1>Disaster Management System</h1>
            <a href="/user">Report Incident</a><br>
            <a href="/admin">Admin Panel</a>
        </body>
        </html>
        """
    elif name == 'user.html':
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Report Incident</h2>
            <form method="POST">
                <input type="text" name="name" placeholder="Your Name"><br>
                <input type="number" name="count" placeholder="Number of people"><br>
                <input type="text" name="coordinates" placeholder="Location"><br>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """
    elif name == 'admin.html':
        reports_html = ""
        for report in reports:
            reports_html += f"""
            <div>
                <p>Name: {report['name']}</p>
                <p>Count: {report['count']}</p>
                <p>Location: {report['coordinates']}</p>
                <p>Time: {report['timestamp']}</p>
                <p>Status: {'Solved' if report['solved'] else 'Pending'}</p>
                <form method="POST" action="/admin_action">
                    <input type="hidden" name="report_id" value="{report['id']}">
                    <input type="submit" name="action" value="solve">
                    <input type="submit" name="action" value="delete">
                </form>
            </div>
            """
        return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Admin Panel</h2>
            {reports_html}
        </body>
        </html>
        """
    return ""

def web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    while True:
        conn, addr = s.accept()
        print('Got connection from', addr)
        request = conn.recv(1024)
        method, path = parse_request(request)
        
        response = ""
        
        if path == '/':
            response = create_response(content=render_template('home.html'))
        
        elif path == '/user':
            if method == 'GET':
                response = create_response(content=render_template('user.html'))
            elif method == 'POST':
                data = handle_post_data(request.decode())
                if 'name' in data and 'count' in data and 'coordinates' in data:
                    reports.append({
                        'name': data['name'],
                        'count': data['count'],
                        'coordinates': data['coordinates'],
                        'timestamp': time.localtime(),
                        'solved': False,
                        'id': len(reports)
                    })
                    response = create_response(status="302 Found", 
                                            content="Redirecting to home...",
                                            content_type="text/plain")
        
        elif path == '/admin':
            if method == 'GET':
                response = create_response(content=render_template('admin.html'))
        
        elif path == '/admin_action':
            if method == 'POST':
                data = handle_post_data(request.decode())
                if 'action' in data and 'report_id' in data:
                    report_id = int(data['report_id'])
                    if data['action'] == 'solve':
                        for report in reports:
                            if report['id'] == report_id:
                                report['solved'] = True
                    elif data['action'] == 'delete':
                        reports[:] = [r for r in reports if r['id'] != report_id]
                response = create_response(status="302 Found", 
                                        content="Redirecting to admin...",
                                        content_type="text/plain")
        
        if not response:
            response = create_response(status="404 Not Found", 
                                    content="Page not found",
                                    content_type="text/plain")
        
        conn.send(response.encode('utf-8'))
        conn.close()

def main():
    ap = setup_ap()
    print(f"Connect to WiFi network '{SSID}' with password '{PASSWORD}'")
    print("Then visit http://192.168.4.1 in your web browser")
    web_server()

if __name__ == '__main__':
    main() 