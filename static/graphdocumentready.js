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
    console.log(numberOfSamples);
    interleave = $('#inputInterleave').val();
    autoupdate = $('#autoupdate').val();
    updateinterval = $('#updateinterval').val();
    updateintervalint = Number(updateinterval);

    $('#reloadCharts').click(function(){
        console.log("User clicked reload");
        updateDisplay();
    });


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