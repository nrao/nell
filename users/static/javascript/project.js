$(document).ready(function() {
	$('#calendar').fullCalendar({
        draggable: false,
        timeFormat: 'H:i',
        events: event_url,
        unavailable: unavailable_url,
        // Clicking on a day provides feedback as to why that day
        // may not be available for observing.
        dayClick: function(td) {
            if ($(this).is('.unavailable')) {
                // This day is unavailable, so make a JSON request to 
                // find out why.
                var data = {};
                data["date"] = Math.round(td.getTime() / 1000) 
                $.getJSON( unavailable_details_url, data, function(data, textStatus, jqXHR) {
                    // parse the JSON and report to user
                    var msg = "";
                    var pcode = data["pcode"];
                    var dt = data["date"];
                    msg = "Reasons that project " + pcode + " cannot observe on " + dt + ".";
                    alert(msg);
                });
            }
        }    

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
