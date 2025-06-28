#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <vector>

// Network credentials
const char* ssid = "DisasterManagement";
const char* password = "123456789";

// Admin password
const char* admin_password = "admin123";

// DNS Server
const byte DNS_PORT = 53;
IPAddress apIP(192, 168, 4, 1);  // ESP32 IP
DNSServer dnsServer;
WebServer webServer(80);

// Data structure for reports
struct Report {
    String name;
    int count;
    String coordinates;
    String timestamp;
    bool solved;
    int id;
};

// In-memory storage for reports
std::vector<Report> reports;

// HTML Templates
const char* HOME_PAGE = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Disaster Communication System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .button {
            display: inline-block;
            padding: 15px 30px;
            margin: 20px;
            font-size: 18px;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            cursor: pointer;
            border: none;
        }
        .admin-btn { background-color: #e74c3c; }
        .user-btn { background-color: #3498db; }
        .button:hover { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Disaster Communication System</h1>
        <p>Please select your role:</p>
        <a href="/admin" class="button admin-btn">Admin</a>
        <a href="/user" class="button user-btn">User</a>
    </div>
</body>
</html>
)";

const char* USER_PAGE = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Submit Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #3498db;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Submit Your Information</h1>
        <form method="POST" action="/submit">
            <div class="form-group">
                <label for="name">Your Name:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="count">Number of people with you:</label>
                <input type="number" id="count" name="count" min="1" required>
            </div>
            <div class="form-group">
                <label for="coordinates">Location Coordinates:</label>
                <input type="text" id="coordinates" name="coordinates" required>
            </div>
            <button type="submit">Submit</button>
        </form>
    </div>
</body>
</html>
)";

const char* ADMIN_LOGIN = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #e74c3c; text-align: center; }
        input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 4px;
            width: 100%;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Login</h1>
        <form method="POST" action="/admin">
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
)";

// Function to generate admin page with current reports
String generateAdminPage() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #e74c3c; text-align: center; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .solved { background-color: #e8f5e9; }
        .action-btn {
            padding: 5px 10px;
            margin: 2px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            color: white;
        }
        .solve-btn { background-color: #2ecc71; }
        .delete-btn { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Dashboard</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>People</th>
                <th>Location</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
    )";

    for (const Report& report : reports) {
        html += "<tr class='" + String(report.solved ? "solved" : "") + "'>";
        html += "<td>" + report.name + "</td>";
        html += "<td>" + String(report.count) + "</td>";
        html += "<td>" + report.coordinates + "</td>";
        html += "<td>" + report.timestamp + "</td>";
        html += "<td>" + String(report.solved ? "Solved" : "Pending") + "</td>";
        html += "<td>";
        if (!report.solved) {
            html += "<form style='display:inline' method='POST' action='/admin_action'>";
            html += "<input type='hidden' name='action' value='solve'>";
            html += "<input type='hidden' name='id' value='" + String(report.id) + "'>";
            html += "<button class='action-btn solve-btn'>Solve</button>";
            html += "</form>";
        }
        html += "<form style='display:inline' method='POST' action='/admin_action'>";
        html += "<input type='hidden' name='action' value='delete'>";
        html += "<input type='hidden' name='id' value='" + String(report.id) + "'>";
        html += "<button class='action-btn delete-btn'>Delete</button>";
        html += "</form>";
        html += "</td></tr>";
    }

    html += R"(
        </table>
    </div>
</body>
</html>
    )";
    return html;
}

const char* SUCCESS_PAGE = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Success</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2ecc71; }
        .home-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✓ Success!</h1>
        <p>Your information has been received.</p>
        <p>Help will be sent to your location as soon as possible.</p>
        <a href="/" class="home-link">Return to Home</a>
    </div>
</body>
</html>
)";

String getFormValue(String data, String key) {
    int start = data.indexOf(key + "=");
    if (start == -1) return "";
    start += key.length() + 1;
    int end = data.indexOf("&", start);
    if (end == -1) end = data.length();
    return data.substring(start, end);
}

void handleSubmit() {
    if (webServer.method() != HTTP_POST) {
        webServer.send(405, "text/plain", "Method Not Allowed");
        return;
    }

    String name = getFormValue(webServer.arg("plain"), "name");
    String countStr = getFormValue(webServer.arg("plain"), "count");
    String coordinates = getFormValue(webServer.arg("plain"), "coordinates");
    
    if (name == "" || countStr == "" || coordinates == "") {
        webServer.send(400, "text/plain", "Missing required fields");
        return;
    }

    // Get current time
    time_t now;
    time(&now);
    struct tm timeinfo;
    localtime_r(&now, &timeinfo);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);

    // Create new report
    Report report;
    report.name = name;
    report.count = countStr.toInt();
    report.coordinates = coordinates;
    report.timestamp = String(timestamp);
    report.solved = false;
    report.id = reports.size();
    
    reports.push_back(report);
    
    webServer.send(200, "text/html", SUCCESS_PAGE);
}

void handleAdminAction() {
    if (webServer.method() != HTTP_POST) {
        webServer.send(405, "text/plain", "Method Not Allowed");
        return;
    }

    String action = getFormValue(webServer.arg("plain"), "action");
    int id = getFormValue(webServer.arg("plain"), "id").toInt();

    for (Report& report : reports) {
        if (report.id == id) {
            if (action == "solve") {
                report.solved = true;
            } else if (action == "delete") {
                reports.erase(reports.begin() + (&report - &reports[0]));
            }
            break;
        }
    }

    // Redirect back to admin page
    webServer.sendHeader("Location", "/admin");
    webServer.send(303);
}

void setup() {
    Serial.begin(115200);
    
    // Configure access point
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
    WiFi.softAP(ssid, password);

    // Start DNS server
    dnsServer.start(DNS_PORT, "*", apIP);

    Serial.println("Access Point Started");
    Serial.print("SSID: ");
    Serial.println(ssid);
    Serial.print("Password: ");
    Serial.println(password);
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.softAPIP());

    // Setup web server routes
    webServer.on("/", HTTP_GET, []() {
        webServer.send(200, "text/html", HOME_PAGE);
    });

    webServer.on("/user", HTTP_GET, []() {
        webServer.send(200, "text/html", USER_PAGE);
    });

    webServer.on("/submit", HTTP_POST, handleSubmit);

    webServer.on("/admin", HTTP_GET, []() {
        webServer.send(200, "text/html", ADMIN_LOGIN);
    });

    webServer.on("/admin", HTTP_POST, []() {
        String password = getFormValue(webServer.arg("plain"), "password");
        if (password == admin_password) {
            webServer.send(200, "text/html", generateAdminPage());
        } else {
            webServer.send(401, "text/html", ADMIN_LOGIN);
        }
    });

    webServer.on("/admin_action", HTTP_POST, handleAdminAction);

    // Handle not found - redirect to home
    webServer.onNotFound([]() {
        webServer.sendHeader("Location", "/");
        webServer.send(302);
    });
    
    webServer.begin();
    Serial.println("HTTP server started");
}

void loop() {
    dnsServer.processNextRequest();
    webServer.handleClient();
} 