$(document).ready(function() {

    console.log("Document ready **************************")

    // update hostname
    $.getJSON('/serverinfo', function(d) {
        $('#hostname').html(d.hostname);
    });

    $('#inputNumberSamples').val(numberOfSamples);
    $('#inputInterleave').val(interleave);
    $('#updateinterval').val(updateinterval);

    updateCurrentTemperature()

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

    drawCharts(numberOfSamples, interleave);
});