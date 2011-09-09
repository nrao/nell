$(document).ready(function() {
	$('#calendar').fullCalendar({
        draggable: false,
        timeFormat: 'H:i',
        events: event_url,
        unavailable: unavailable_url
	});
    $('.checkable').click(function() {
      var checked = $(this).attr("checked");
      if (checked == 'true') {
        $(this).attr("src", "/static/images/unchecked.png");
        $(this).attr("checked", "false");
      } else {
        $(this).attr("src", "/static/images/checked.png");
        $(this).attr("checked", "true");
      }
      var uri = $(this).attr("href");
      $.ajax({
        type: "POST",
        url:  uri,
      });
    });
});
