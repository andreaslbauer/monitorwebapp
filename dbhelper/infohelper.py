from dbhelper import sqlhelper
from datetime import datetime


# read rows to find out how many different sensors are generating data
def numberSensors(db):

    # get the DB info
    rowCount = sqlhelper.countRows(db)

    # count sensors by looking at rows
    sensorCount = 0
    rowidx = rowCount
    row = sqlhelper.getRow(db, rowidx)
    lastSensorId = row[1]
    currentSensorId = -1
    while (lastSensorId != currentSensorId) and (rowidx > 0):
        rowidx = rowidx - 1
        row = sqlhelper.getRow(db, rowidx)
        currentSensorId = row[1]
        sensorCount = sensorCount + 1

    return sensorCount


# determine time between sensor reads - in seconds

def timeBetweenSensorReads(db):

    # get the DB info
    rowCount = sqlhelper.countRows(db)
    row = sqlhelper.getRow(db, rowCount)
    sensorCount = numberSensors(db)
    timeStampLast = row[4]
    row = sqlhelper.getRow(db, rowCount - sensorCount)
    timeStampLastBefore = row[4]

    date_format = "%Y-%m-%d %H:%M:%S.%f"
    d1 = datetime.strptime(timeStampLastBefore, date_format)
    d2 = datetime.strptime(timeStampLast, date_format)
    seconds = int((d2 -d1).total_seconds())

    return seconds

def getChange(db, rangeInbetween = 10):
    # compute the change
    timeBetween = timeBetweenSensorReads(db)
    rowCount = sqlhelper.countRows(db)
    sensorCount = numberSensors(db)

    # get the last 6 rows
    offset = sensorCount * rangeInbetween
    lastRows = sqlhelper.getRows(db, rowCount - sensorCount, rowCount)
    beforeRows = sqlhelper.getRows(db, rowCount - sensorCount - offset, rowCount - offset)

    # set up a return list that has change for each sensor
    changeList = [None] * sensorCount
    for i in range(0, sensorCount):
        sensorId = lastRows[i][1]
        valueLast = lastRows[sensorId][5]
        valueBefore = beforeRows[sensorId][5]
        changeList[sensorId - 1] = valueLast - valueBefore

    return changeList


def getChanges(db, numberRows, timeInterleave = 10):
    # compute the change
    timeBetween = timeBetweenSensorReads(db)
    rangeInbetween = int(timeInterleave / (timeBetween + 1))
    rowCount = sqlhelper.countRows(db)
    sensorCount = numberSensors(db)

    # get the last 6 rows
    offset = sensorCount * rangeInbetween
    rows = []
    for rowIndex in range(0, numberRows):
        offsetIndex = offset * rowIndex
        rows.append(sqlhelper.getRows(db, rowCount - sensorCount - offsetIndex + 1, rowCount - offsetIndex))

    # set up a return list that has change for each sensor
    changeArray = []

    for rowIndex in range(0, numberRows):
        changeArray.append([None] * (sensorCount + 1))
        changeArray[rowIndex][0] = rows[rowIndex][1][3]
        for sensor in range(0, sensorCount):
            sensorId = rows[rowIndex][sensor][1]
            v = round(rows[rowIndex][sensorId - 1][5], 1)
            changeArray[rowIndex][sensorId] = v


    return changeArray
