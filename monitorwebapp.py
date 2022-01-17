#!/usr/bin/python3

#
# Flask Web App to implement web pages and REST endpoints for measurement display
# Requires Flask and Flask-Rest
#

import logging
# set up the logger
logging.basicConfig(filename="/tmp/monitorwebapp.log", format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

from flask import Flask, jsonify
from flask import render_template
from flask_restful import Resource, Api, fields, marshal_with, reqparse, marshal
from flask_executor import Executor
# logging facility: https://realpython.com/python-logging/
import os
import time

# sqlite3 access API

import datetime
import socket
import requests
from dbhelper import sqlhelper
from dbhelper import infohelper
from dbhelper import dataaccess
import threading
import shutil


app = Flask(__name__)
api = Api(app)
executor = Executor(app)
parser = reqparse.RequestParser()
OurHostname = ""


# resource field mapping used when marshalling data
resourceFields = {
    'id':       fields.Integer,
    'sensorid': fields.Integer,
    'date':     fields.String,
    'time':     fields.String,
    'isodatetime': fields.String,
    'value':    fields.Float
}

def shutdownCMD():
    time.sleep(2)
    logging.info("Shutting down...")
    os.system('sudo shutdown 1')

def rebootCMD():
    time.sleep(2)
    logging.info("Rebooting...")
    os.system('sudo reboot 1')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/current')
def current():
    return render_template('current.html')

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')

@app.route('/reboot')
def reboot():
    executor.submit(rebootCMD)
    return render_template('reboot.html')

@app.route('/shutdown')
def shutdown():
    executor.submit(shutdownCMD)
    return render_template('shutdown.html')

# option to rename and delete the db file
@app.route('/resetdb')
def resetdb():
    filename = sqlhelper.dbfilename
    nowdatetime = datetime.datetime.now()
    d = nowdatetime.strftime("%Y_%m_%d_%H_%M_%S")
    newfilename = filename + "." + d
    shutil.copyfile(filename, newfilename)
    logging.info("Rename database file to %s", newfilename)
    os.remove(filename)
    logging.info("Delete database file to %s", filename)

    return render_template('resetdb.html')

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

@app.route('/webapplog')
def webapplog():
    f = open("/tmp/monitorwebapp.log", "r")

    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Web App Log</h1><hr><br><pre>"

    for line in f:
        page = page + line

    page = page + "</pre></html>"
    return page

@app.route('/summary')
def summary():
    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Web Thermometer Sensor Summary</h1><hr><br>"

    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    rowCount = sqlhelper.countRows(db)
    page = page + "Number of data points in table: " + str(rowCount) + '<p>'
    row = sqlhelper.getRow(db, rowCount)

    # display how many sensor are collecting data
    sensorCount = infohelper.numberSensors(db)
    page = page + "Number of sensors: " + str(sensorCount) + '<p>'

    # display how many sensor are collecting data
    rateOfChange = infohelper.getRateOfChange(db)
    page = page + "Rate of change: " + str(rateOfChange) + '<p>'

    # display time elapsed between sensor writes
    timeBetweenReads = infohelper.timeBetweenSensorReads(db)
    page = page + "Time between sensor reads: " + str(timeBetweenReads) + '<p>'

    # display trends over past 10 mins
    rows = sqlhelper.getRows(db, rowCount - 12, rowCount)
    page = page + "Last 12 rows: <p>"
    for r in rows:
        page = page + str(r) + '<p>'

    page = page + "Last data point: " + str(row) + '<p>'
    db.close()

    page = page + "</html>"
    return page

# render table that shows values for all sensor
@app.route('/changes')
def changes():
    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    a = infohelper.getChanges(db, 15, 10 * 60)
    return render_template('changes.html', data = a, lastupdated = a[0][0])


@app.route('/db.csv')
def csv():
    # return all data as CSV (comma seperated values)
    page = ""

    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    numrows = sqlhelper.countRows(db)
    for id in range(0, numrows):
        row = sqlhelper.getRow(db, id)

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
        row = sqlhelper.getLastRowForSensor(sensorid)
        return DataPointDAO(row)

# Data Point object.  Use to marshal several data rows
class DataPoints(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid):
        rows = sqlhelper.getAllRowsForSensor(sensorid)
        dataPoints = []
        for row in rows:
            dataPoints.append(DataPointDAO(row))
        return dataPoints

class DataPointsToday(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid):
        now = datetime.datetime.now()
        nowDate = now.strftime("%Y-%m-%d")
        rows = sqlhelper.getAllRowsBySensorByDate(sensorid, nowDate)
        dataPoints = []
        for row in rows:
            dataPoints.append(DataPointDAO(row))
        return dataPoints

# get the last n data points but skip as many as indicated by interleave inbetween
class DataPointsLastN(Resource):
    @marshal_with(resourceFields)
    def get(self, sensorid, numberRows, interleave):
        rows = dataaccess.getLastNRowsBySensor(sensorid, numberRows * interleave)
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

# get the change information
class ValueChange(Resource):

    def get(self, sensorid, numberrows):
        db = sqlhelper.createConnection(sqlhelper.dbfilename)
        changes = infohelper.getChange(db, numberrows)
        timeBetweenReads = infohelper.DataInfo.dataInfo.timeBetweenSensorReads * numberrows
        change = changes[sensorid - 1]
        rateOfChange = (60 * 60 * change) / timeBetweenReads
        return jsonify({'change': change,
                        'rateOfChange' : rateOfChange})

# get the server hostname
class ServerInfo(Resource):

    def get(self):
        return jsonify({'hostname': OurHostname})

class DataInfo(Resource):

    def get(self):
        datainfo = {}
        datainfo["numSensors"] =  infohelper.DataInfo.dataInfo.numberOfSensors
        datainfo["timeBetweenUpdates"] =  infohelper.DataInfo.dataInfo.timeBetweenSensorReads
        return jsonify(datainfo)

# add REST end points
api.add_resource(DataPoint, '/datapoint/<int:sensorid>')
api.add_resource(DataPoints, '/datapoints/<int:sensorid>')
api.add_resource(DataPointsToday, '/datapoints/today/<int:sensorid>')
api.add_resource(DataPointsLastN, '/datapoints/<int:sensorid>/<int:numberRows>/<int:interleave>')
api.add_resource(ValueChange, '/datachange/<int:sensorid>/<int:numberrows>')
api.add_resource(ServerInfo, '/serverinfo')
api.add_resource(DataInfo, '/datainfo')

# the main routine
if __name__ == '__main__':


    # log start up message
    logging.info("***************************************************************")
    logging.info("Web Monitor Application has started")
    logging.info("Running %s", __file__)
    logging.info("Working directory is %s", os.getcwd())
    logging.info("SQLITE Database file is %s", sqlhelper.dbfilename)

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

    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    app.run(debug=True, host='0.0.0.0')

