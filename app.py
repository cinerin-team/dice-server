from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)


# Adatbázis inicializálása
def init_db():
    conn = sqlite3.connect('devices.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT NOT NULL,
            date DATE NOT NULL,
            status TEXT DEFAULT 'green'
        )
    ''')
    conn.commit()
    conn.close()


# Régi bejegyzések törlése
def delete_old_entries():
    one_month_ago = datetime.now() - timedelta(days=30)
    conn = sqlite3.connect('devices.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM devices WHERE date < ?', (one_month_ago.strftime('%Y-%m-%d'),))
    conn.commit()
    conn.close()


# Alkalmazás inicializáláskor meghívja az adatbázist
init_db()


# Regisztráció végpont (MAC-címek fogadása)
@app.route('/register', methods=['POST'])
def register_device():
    data = request.json
    mac_address = data.get('mac_address')
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Töröljük a régi bejegyzéseket
    delete_old_entries()

    conn = sqlite3.connect('devices.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO devices (mac_address, date) VALUES (?, ?)', (mac_address, date))
    conn.commit()
    conn.close()
    return jsonify({"message": "Device registered"}), 201


# Állapot lekérése
@app.route('/check_status', methods=['GET'])
def check_status():
    mac_address = request.args.get('mac_address')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    conn = sqlite3.connect('devices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices WHERE mac_address = ? AND date = ?', (mac_address, date))
    devices = cursor.fetchall()
    conn.close()

    for device in devices:
        # Frissítsük az állapotot pirosra, ha szükséges
        update_status(device[0], 'red')

    return jsonify({"message": "Status updated to red for matching devices"}), 200


def update_status(device_id, status):
    conn = sqlite3.connect('devices.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE devices SET status = ? WHERE id = ?', (status, device_id))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.4')