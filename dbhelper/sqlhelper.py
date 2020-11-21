# SQLLite DB helpers

import sqlite3
import logging
import sys

# set the filename for the SQLite DB
dbfilename = ""
if sys.platform.startswith('win') :
    logging.info("Running on Windows")
    dbfilename = "c:\workspaces\data.db"
else :
    logging.info("Running on Linux")
    dbfilename = "/home/pi/pimon/data.db"

# create connection to our db
def createConnection(dbFileName):
    """ create a database connection to a SQLite database """
    db = None
    try:
        db = sqlite3.connect(dbFileName)
        return db
    except sqlite3.Error as e:
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

    except sqlite3.Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get row count of table datapoints")

        return 0


# get specific row
def getRow(mydb, id):
    try:
        cursor = mydb.cursor()
        cursor.execute('''SELECT * FROM datapoints WHERE id=?''', (id,))
        return cursor.fetchone()

    except sqlite3.Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

        return 0


# get specific row
def getRows(mydb, fromId, toId):
    try:
        cursor = mydb.cursor()
        cursor.execute('''SELECT * FROM datapoints WHERE id>=? and id<=?''', (fromId, toId,))
        return cursor.fetchall()

    except sqlite3.Error as e:
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

    except sqlite3.Error as e:
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

    except sqlite3.Error as e:
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

    except sqlite3.Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None

