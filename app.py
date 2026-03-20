from flask import Flask, request, render_template_string
import requests
import csv
from datetime import datetime
import pytz
import os

app = Flask(__name__)

LOG_FILE = "logs.csv"

# Ensure CSV file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["IP", "User-Agent", "City", "Country", "ISP", "Timestamp"])


def get_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def get_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")


@app.route('/spills')
def consent_page():
    return render_template_string("""
        <h2>Cybersecurity Demo</h2>
        <p>This page collects basic device information for educational purposes.</p>
        <a href="/fool"><button>Continue</button></a>
    """)


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

    # Save to CSV
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ip, user_agent, city, country, isp, timestamp])

    return """
        <h2>Data Collected Successfully</h2>
        <p>This was part of a cybersecurity awareness demo.</p>
    """


@app.route('/logs')
def view_logs():
    try:
        with open("logs.csv", "r") as file:
            rows = file.readlines()

        table = "<table border='1'>"
        for row in rows:
            table += "<tr>" + "".join(f"<td>{col.strip()}</td>" for col in row.split(",")) + "</tr>"
        table += "</table>"

        return table
    except:
        return "No logs available yet."


if __name__ == '__main__':
    app.run(debug=True)
