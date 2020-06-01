#!/usr/bin/python3

#
# Flask Web App to implement web pages and REST endpoints for measurement display
# Requires Flask and Flask-Rest
#

from flask import Flask, jsonify
from flask import render_template
from flask_restful import Resource, Api, fields, marshal_with, reqparse, marshal
# logging facility: https://realpython.com/python-logging/
import logging
import os

# sqlite3 access API
import sqlite3
from sqlite3 import Error
import datetime
import sys
import socket
import requests

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
OurHostname = ""

# set the filename for the SQLite DB
dbfilename = ""
if sys.platform.startswith('win') :
    logging.info("Running on Windows")
    dbfilename = "c:\workspaces\data.db"
else :
    logging.info("Running on Linux")
    dbfilename = "/home/pi/pimon/data.db"


# resource field mapping used when marshalling data
resourceFields = {
    'id':       fields.Integer,
    'sensorid': fields.Integer,
    'date':     fields.String,
    'time':     fields.String,
    'isodatetime': fields.String,
    'value':    fields.Float
}

# create connection to our db
def createConnection(dbFileName):
    """ create a database connection to a SQLite database """
    db = None
    try:
        db = sqlite3.connect(dbFileName)
        return db
    except Error as e:
        logging.error("Unable to create database connection to %s", dbFileName)
        if db != None:
            db.close()

    return None

# get number of rows in table
def countRows(mydb):
    sql = '''select count(*) from datapoints'''
    try:
        cursor = mydb.cursor()
        result = cursor.execute(sql).fetchone()
        return result[0]

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get row count of table datapoints")

        return 0


# get specific row
def getRow(mydb, id):
    try:
        cursor = mydb.cursor()
        cursor.execute('''SELECT * FROM datapoints WHERE id=?''', (id,))
        return cursor.fetchone()

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

        return 0


# get specific row
def getRows(mydb, fromId, toId):
    try:
        cursor = mydb.cursor()
        cursor.execute('''SELECT * FROM datapoints WHERE id>=? and id<=?''', (fromId, toId,))
        return cursor.fetchall()

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

        return 0

# get the last data point for a given sensor
def getLastRowForSensor(sensorId):
    try:
        logging.info("Get last data point for sensor %s", sensorId)
        mydb = createConnection(dbfilename)
        cursor = mydb.cursor()
        sql = '''select count(*) from datapoints'''
        result = cursor.execute(sql).fetchone()
        lastRow = result[0]
        cursor.execute('''SELECT * FROM datapoints WHERE sensorid=? and id>=? and id<=?''', (sensorId, lastRow - 5, lastRow,))
        row = cursor.fetchone()
        mydb.close()
        return row

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None

# get specific row
def getLastNRowsBySensor(sensorId, rowCount):
    try:
        logging.info("Get last %s data points for sensor %s", rowCount, sensorId)
        mydb = createConnection(dbfilename)
        cursor = mydb.cursor()
        sql = '''select count(*) from datapoints'''
        result = cursor.execute(sql).fetchone()
        lastRow = result[0]
        cursor.execute('''SELECT * FROM datapoints WHERE sensorid=? and id>=? and id<=?''',
                       (sensorId, lastRow - (6 * rowCount), lastRow,))
        row = cursor.fetchall()
        mydb.close()
        return row

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None


# get all data points for a given sensor
def getAllRowsForSensor(sensorId):
    try:
        logging.info("Get last data point for sensor %s", sensorId)
        mydb = createConnection(dbfilename)
        cursor = mydb.cursor()
        sql = '''select count(*) from datapoints'''
        result = cursor.execute(sql).fetchone()
        lastRow = result[0]
        cursor.execute('''SELECT * FROM datapoints WHERE sensorid=? order by id''', (sensorId,))
        rows = cursor.fetchall()
        mydb.close()
        return rows

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None

# get all data points for a given sensor
def getAllRowsBySensorByDate(sensorId, date):
    try:
        logging.info("Get all data points for sensor %s and %s", sensorId, date)
        mydb = createConnection(dbfilename)
        cursor = mydb.cursor()
        sql = '''select count(*) from datapoints'''
        result = cursor.execute(sql).fetchone()
        lastRow = result[0]
        cursor.execute('''SELECT * FROM datapoints WHERE sensorid=? and date=? order by id''', (sensorId, date,))
        rows = cursor.fetchall()
        mydb.close()
        return rows

    except Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/current')
def current():
    return render_template('current.html')

@app.route('/summarycharts')
def summarycharts():
    return render_template('summarycharts.html')

@app.route('/detailedcharts')
def detailedcharts():
    return render_template('detailedcharts.html')

@app.route('/datacollectorlog')
def datacollectorlog():
    f = open("/tmp/datacollector.log", "r")

    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Data Collector Log</h1><hr><br><pre>"

    for line in f:
        page = page + line

    page = page + "</pre></html>"
    return page

@app.route('/servicecontrollerlog')
def servicecontrollerlog():
    f = open("/tmp/servicecontroller.log", "r")

    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Service Controller Log</h1><hr><br><pre>"

    for line in f:
        page = page + line

    page = page + "</pre></html>"
    return page

@app.route('/summary')
def summary():
    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Web Thermometer Sensor Summary</h1><hr><br>"

    db = createConnection(dbfilename)
    rowCount = countRows(db)
    page = page + "Number of data points in table: " + str(rowCount) + '<p>'
    row = getRow(db, rowCount)

    rows = getRows(db, rowCount - 24, rowCount)
    page = page + "Last 24 rows: <p>"
    for r in rows:
        page = page + str(r) + '<p>'

    page = page + "Last data point: " + str(row) + '<p>'
    db.close()

    page = page + "</html>"
    return page

@app.route('/db.csv')
def csv():
    # return all data as CSV (comma seperated values)
    page = ""

    db = createConnection(dbfilename)
    numrows = countRows(db)
    for id in range(0, numrows):
        row = getRow(db, id)

        #print(row)
        if row != None:
            channel = row[1]
            if (channel == 1):
                datestamp = row[2]
                timestamp = row[3]
                page = page + "\n"
                page = page + datestamp + ' ' + timestamp

            page = page + ", " + str(row[5])

    return page

# Data Access Object to wrap a row into a data point object
class DataPointDAO(object):
    def __init__(self, row):
        self.id = row[0]
        self.sensorid =row[1]
        self.date = row[2]
        self.time = row[3]
        self.isodatetime = row[4]
        self.value = row[5]

# Data Point object.  Use to marshal a data row
class DataPoint(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid):
        row = getLastRowForSensor(sensorid)
        return DataPointDAO(row)

# Data Point object.  Use to marshal several data rows
class DataPoints(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid):
        rows = getAllRowsForSensor(sensorid)
        dataPoints = []
        for row in rows:
            dataPoints.append(DataPointDAO(row))
        return dataPoints

class DataPointsToday(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid):
        now = datetime.datetime.now()
        nowDate = now.strftime("%Y-%m-%d")
        rows = getAllRowsBySensorByDate(sensorid, nowDate)
        dataPoints = []
        for row in rows:
            dataPoints.append(DataPointDAO(row))
        return dataPoints

# get the last n data points but skip as many as indicated by interleave inbetween
class DataPointsLastN(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid, numberRows, interleave):
        rows = getLastNRowsBySensor(sensorid, numberRows)
        dataPoints = []
        count = 0

        # append the data rows to the return data set - but leave out rows as specified by the interleave num
        for row in rows:
            count = count + 1
            #print(count)
            if count >= interleave:
                dataPoints.append(DataPointDAO(row))
                count = 0
                
        return dataPoints


# get the last n data points but skip as many as indicated by interleave inbetween
class ServerInfo(Resource):

#    model = {
#        'hostname' : fields.String
#    }

#    @marshal_with(model)
    def get(self):
        return jsonify({'hostname': OurHostname})



# add REST end points
api.add_resource(DataPoint, '/datapoint/<int:sensorid>')
api.add_resource(DataPoints, '/datapoints/<int:sensorid>')
api.add_resource(DataPointsToday, '/datapoints/today/<int:sensorid>')
api.add_resource(DataPointsLastN, '/datapoints/<int:sensorid>/<int:numberRows>/<int:interleave>')
api.add_resource(ServerInfo, '/serverinfo')

# the main routine
if __name__ == '__main__':
    print("Starting Web Monitor Application")

    # set up the logger
    # logging.basicConfig(filename="/tmp/monitorwebapp.log", format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # log start up message
    logging.info("***************************************************************")
    logging.info("Web Monitor Application has started")
    logging.info("Running %s", __file__)
    logging.info("Working directory is %s", os.getcwd())
    logging.info("SQLITE Database file is %s", dbfilename)

    try:
        hostname = socket.gethostname()
        OurHostname = hostname
        externalip = requests.get('https://api.ipify.org').text
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        localipaddress = s.getsockname()[0]
        logging.info("Hostname is %s", hostname)
        logging.info("Local IP is %s and external IP is %s", localipaddress, externalip)

    except Exception as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get network information")

    db = createConnection(dbfilename)
    app.run(debug=True, host='0.0.0.0')

