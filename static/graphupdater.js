
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

function setUpdateTimer() {

    updateinterval = $('#updateinterval').val();
    updateintervalint = Number(updateinterval) * 1000;
    autoupdate = $('#autoupdate').is(':checked');
    console.log('Set update timer: ', updateintervalint, autoupdate, " at ", new Date().toLocaleString());

    // set interval to reload every 60s if checkbox for auto-reload is checked
    setTimeout(function() {
        autoupdate = $('#autoupdate').is(':checked');
        console.log('Update timer fired: ', updateintervalint, autoupdate, " at ", new Date().toLocaleString());
        if (autoupdate) {
          updateDisplay();
        }
    }, updateintervalint);
}

function updateDisplay() {
    console.log("Reload charts");
    numberOfSamples = $('#inputNumberSamples').val();
    interleave = $('#inputInterleave').val();
    updateCurrentTemperature(numberOfSensors)
    drawCharts(numberOfSamples, interleave, numberOfSensors, chartstyle);

    // set update timer to redraw automatically (if checkbox checked)
    setUpdateTimer();
}
