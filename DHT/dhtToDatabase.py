import Adafruit_DHT
import sqlite3
import datetime
from time import sleep

# DHT
sensor = Adafruit_DHT.DHT11
pin = 23

# Connection
conn = sqlite3.connect('humidtemps.db')

# Insert function
def insertIntoDB():
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
        conn.commit()

while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('Failed to get reading. Try again!')
        
    insertIntoDB()
    print("Inserted to DB")
    sleep(10)
