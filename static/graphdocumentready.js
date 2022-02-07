var intervalId;

function updateCurrentTemperature(numberOfSensors) {
    for (var i = 1; i <= numberOfSensors; i++) {
        let s = i.toString();
        $.getJSON(ip + '/datapoint/' + s, function(d) {
            var tag = '#currentTemp' + s;
            $(tag).html(d.value.toFixed(2));
            $(currentLastUpdated).html(d.time);
            lastupdatetime = d.time;
      });
    };
};

function updateDisplay() {
    console.log("Reload charts");
    numberOfSamples = $('#inputNumberSamples').val();
    interleave = $('#inputInterleave').val();
    updateCurrentTemperature(numberOfSensors)
    drawCharts(numberOfSamples, interleave, numberOfSensors, chartstyle);
}

function checkSetAutoUpdate() {
    // automatically update if checked
    autoupdatecheck = $('#autoupdate').is(':checked');
    if (autoupdatecheck) {
        updateinterval = $('#updateinterval').val();
        updateintervalint = Number(updateinterval);
        intervalId = setInterval(updateDisplay, updateintervalint * 1000);
        console.log("Turn on automatic update at: ", updateintervalint);
    } else {
        console.log("Check whether automatic update is on");
        if (intervalId) {
            clearInterval(intervalId);
            console.log("Disable automatic update");
        }
    }
}


$(document).ready(function() {

    console.log("Document ready **************************")

    // update hostname
    $.getJSON('/serverinfo', function(d) {
        $('#hostname').html(d.hostname);
    });

    $('#inputNumberSamples').val(numberOfSamples);
    $('#inputInterleave').val(interleave);
    $('#updateinterval').val(updateinterval);

    numberOfSamples = $('#inputNumberSamples').val();
    interleave = $('#inputInterleave').val();
    autoupdate = $('#autoupdate').val();
    updateinterval = $('#updateinterval').val();
    updateintervalint = Number(updateinterval);

    $.getJSON('/chartconfig', function(d) {
        console.log('Load chart configuration:', d);
        numberOfSamples = d.chartShowNumberSamples;
        interleave = d.chartInterleave;

        $('#inputNumberSamples').val(numberOfSamples);
        $('#inputInterleave').val(interleave);
        $('#updateinterval').val(updateinterval);

        // now load the chart data and draw the chart
        $.getJSON('/datainfo', function(d) {
            let s = "<style>.nobr { white-space: nowrap }</style>";
            numberOfSensors = d.numSensors;

            s = s + "<tr>";
            for (var sensorid = 1; sensorid <= numberOfSensors; sensorid++) {
                newTableRow = false;
                if ((sensorid) % (chartstyle + 1) == 0) { newTableRow = true; }
                if (newTableRow) { s = s + "</tr>"; }

                s = s + "<td><div id=\"channel" + sensorid.toString() + "Status\"></div><div id=\"channel" +
                        sensorid.toString() + "Chart\"></div></td>"

                if (newTableRow) { s = s + "<tr>"; }
            }
            s = s + "</tr>";
            console.log(s);
            $('#charts').html(s);

            // update numbers, draw the charts
            updateCurrentTemperature(numberOfSensors);
            drawCharts(numberOfSamples, interleave, numberOfSensors, chartstyle);
        });
    });

    $('#reloadCharts').click(function(){
        console.log("User clicked reload");
        updateDisplay();
        $.ajax({
            url: '/chartconfig',
            type: 'POST',
            data: {
                chartInterleave: interleave,
                chartShowNumberSamples: numberOfSamples
            },
            success: function(){
                console.log("Chart config was updated");
            }
        })
    });

    $('#autoupdate').click(function(){
        checkSetAutoUpdate();
    });

    checkSetAutoUpdate();
});