$('#distanceRange').prop('disabled', false);
$('#timeRange').prop('disabled', true);

$('input[type=radio][name=radioSegmentType]').change(function() {
    if (this.value == 'distance') {
        $('#distanceRange').prop('disabled', false);
        $('#timeRange').prop('disabled', true);
    }
    else if (this.value == 'time') {
        $('#distanceRange').prop('disabled', true);
        $('#timeRange').prop('disabled', false);
    }
});

function recalculate(){
    const segmentType = $('input[type=radio][name=radioSegmentType]:checked').val();
    const baseUrl = '/analyze/performance' + '?f=' + $('#activityName').text();
    if (segmentType == 'distance') {
        const distance = $('#distanceRange').val();
        const url = baseUrl + '&d=' + distance;
        console.log(url);
        window.open(url,"_self");
    } else if (segmentType == 'time'){
        const time = $('#timeRange').val();
        const url = baseUrl + '&t=' + time;
        console.log(url);
        window.open(url,"_self");
    }
}