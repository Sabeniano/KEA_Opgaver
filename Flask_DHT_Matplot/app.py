import Adafruit_DHT
import sqlite3
import datetime
import schedule
import threading
import base64
from time import sleep
from io import BytesIO
from flask import Flask
from matplotlib.figure import Figure

# Empty lists for database
temp_from_db = []
humid_from_db = []
counter = []

# DHT
sensor = Adafruit_DHT.DHT11
pin = 23

humidity = 0
temperature = 0

def from_db():
    conn = sqlite3.connect('humidtemps.db')
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM humidtemps')
        global temp_from_db
        global humid_from_db
        global counter
        rset = cur.fetchall()
        print(f'Row-count : { len(rset) } ')
        for row in rset:
            counter.append(row[0])
            temp_from_db.append(row[2])
            humid_from_db.append(row[3])
    except sqlite3.Error as e:
        print(f'Error calling SQL:  "{e}"')
    finally:
        conn.close()

def insert_into_db():
    conn = sqlite3.connect('humidtemps.db')

    query = 'INSERT INTO humidtemps (DATETIME, TEMPERATURE, HUMIDITY) VALUES(?,?,?)'
    data = (datetime.datetime.now(), temperature, humidity)
    try:
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not insert into humidtemps ! {e} ')
    finally:
        conn.close()

def get_temp_humid_timer():
    global humidity
    global temperature
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        insert_into_db()
        print("Inserted to DB")
    else:
        print('Failed to get reading. Try again!')

app = Flask(__name__)
@app.route("/")
def flask_to_web():
    fig = Figure()
    ax = fig.subplots()

    ax.set_xlabel('X-Axis')
    ax.set_ylabel('Y-Axis - Celcius')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis = 'x', colors='white')
    ax.tick_params(axis = 'y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')

    temp_y = temp_from_db
    temp_x = counter
    ax.plot(temp_x, temp_y, linestyle='dashed', c='white', linewidth='1.5', marker='X', mec='blue', ms=10, mfc='blue')

    humid_y = humid_from_db
    humid_x = counter
    ax.plot(humid_x, humid_y, linestyle='dashed', c='white', linewidth='1.5', marker='o', mec='red', ms=10, mfc='red')
    
    ax.set_facecolor("#000")
    fig.patch.set_facecolor('#000')

    buf = BytesIO()
    fig.savefig(buf, format="png")

    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src= 'data:image/png;base64,{data}'/>"

def background_task():
    what_day = datetime.datetime.now()

    if what_day.strftime("%A") != "Saturday" or "Sunday":
        schedule.every(20).minutes.do(get_temp_humid_timer)
        schedule.every(20).minutes.do(from_db)
    else:
        schedule.every().day.at("07:00").do(get_temp_humid_timer)
        schedule.every().day.at("07:00").do(from_db)

        schedule.every().day.at("12:00").do(get_temp_humid_timer)
        schedule.every().day.at("12:00").do(from_db)

        schedule.every().day.at("17:00").do(get_temp_humid_timer)
        schedule.every().day.at("17:00").do(from_db)

        schedule.every().day.at("23:00").do(get_temp_humid_timer)
        schedule.every().day.at("23:00").do(from_db)

    while True:
        schedule.run_pending()
        sleep(1)

def start_background_thread():
    thread = threading.Thread(target=background_task)
    thread.start()

start_background_thread()

if __name__ == "__main__":
    from_db()
    app.run('0.0.0.0', port=5000)