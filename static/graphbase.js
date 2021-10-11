
var numberOfSamples = '180';
var interleave = '3';
var autoupdate = false;
var updateinterval = '60';
var numberOfSensors = 0;
//var ip = "http://192.168.0.125:5000";
var ip = '';

var lastupdatetime = 'N/A';

function drawChart(dataURL, statusTag, targetTag, chartTitle) {
    $(statusTag).html("Loading...");

    console.log('Load data from: ', dataURL, ' at ', new Date().toLocaleString(), ' Style: ', chartstyle);

    // use d3 library to load chart data in JSON format
    d3.json(dataURL, function(data) {

        if (data != null) {
            var dataItemCount = data.length;
            console.log('Received data from: ', dataURL, " Received items: ",
                        dataItemCount, ' at ', new Date().toLocaleString());

            // now need to convert the dates for the charting package

            for (var i = 0; i < dataItemCount; i++) {
                var dataItem = data[i];
                var dateObject = new Date(Date.parse(dataItem.isodatetime));
                dataItem.date = dateObject;
            }

            // size chart window width to browers viewport width
            var viewportWidth  = document.documentElement.clientWidth;

            var chartwidth = 0;
            if (chartstyle == 2) {
                chartwidth = (viewportWidth - 32) / 2;
                chartheight = 180;
            } else {
                chartwidth = viewportWidth - 32;
                chartheight = 240;
            }

            //data = MG.convert.date(data, 'date');
            MG.data_graphic({
                title: chartTitle,
                description: "This graphic shows measurements from the Raspberry Pi Sensors",
                data: data,
                area: false,
                width: chartwidth,
                height: chartheight,
                top : 35,
                target: targetTag,
                x_accessor: 'date',
                y_accessor: 'value'
            });

            $(statusTag).html('Last Updated: ' + lastupdatetime);
        } else {
            console.log('No data received from: ', dataURL);
        }
    });
}

function drawCharts(numberOfSamples, interleave, numberOfSensors, chartStyle) {
    console.log("Charts to draw: ", numberOfSensors);
    for (sensorid = 1; sensorid <= numberOfSensors; sensorid ++) {
        let url = ip + '/datapoints/' + sensorid.toString() + '/' + numberOfSamples + '/' + interleave;
        let statusTag = '#channel' + sensorid.toString() + 'Status';
        let targetTag = '#channel' + sensorid.toString() + 'Chart';
        let chartTitle = 'Sensor ' + sensorid.toString();

        drawChart(url, statusTag, targetTag, chartTitle);
    }
};
