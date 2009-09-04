$(document).ready(function() {
	$('#calendar').fullCalendar({
        draggable: false,
        timeFormat: 'H:i',
        events: event_url,
        unavailable: unavailable_url
	});
});
