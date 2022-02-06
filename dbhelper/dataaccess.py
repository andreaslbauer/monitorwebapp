import sqlite3
import logging
from dbhelper import infohelper
from dbhelper import sqlhelper


# get specific row
def getLastNRowsBySensor(sensorId, rowCount):
    try:
        #logging.info("Get last %s data points for sensor %s", rowCount, sensorId)
        mydb = sqlhelper.createConnection(sqlhelper.dbfilename)
        cursor = mydb.cursor()
        sql = '''select count(*) from datapoints'''
        result = cursor.execute(sql).fetchone()
        lastRow = result[0]
        howManyGoBack = infohelper.DataInfo.dataInfo.numberOfSensors * rowCount
        cursor.execute('''SELECT * FROM datapoints WHERE sensorid=? and id>=?''',
                       (sensorId, lastRow - howManyGoBack,))
        rows = cursor.fetchall()
        while (len(rows) > rowCount):
            rows.pop(0)
        mydb.close()
        return rows

    except sqlite3.Error as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get data point %s", id)

    mydb.close()
    return None

