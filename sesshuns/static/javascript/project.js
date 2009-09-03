$(document).ready(function() {
	$('#calendar').fullCalendar({
        draggable: false,
        events: event_url,
        unavailable: unavailable_url
	});
});
