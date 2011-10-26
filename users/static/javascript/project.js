$(document).ready(function() {
	$('#calendar').fullCalendar({
        draggable: false,
        timeFormat: 'H:i',
        events: event_url,
        unavailable: unavailable_url,
        // Clicking on a day provides feedback as to why that day
        // may not be available for observing.
        dayClick: function(td) {
            if ($(this).hasClass('fc-unavailable')) { 
                // This day is unavailable, so make a JSON request to 
                // find out why.
                var data = {};
                data["date"] = Math.round(td.getTime() / 1000) 
                $.getJSON( unavailable_details_url, data, function(data, textStatus, jqXHR) {
                    // parse the JSON and report to user
                    var msg = "";
                    var pcode = data["pcode"];
                    var dt = data["date"];
                    msg = "Reasons that project " + pcode + " cannot observe on " + dt + ":\n";
                    if (data["project_complete"]) {
                        msg += " * Project complete.\n"
                    }
                    if (data["no_enabled_sessions"]) {
                       msg += " * No enabled sessions.\n"
                    }
                    if (data["no_authorized_sessions"]) {
                       msg += " * No authorized sessions.\n"
                    }
                    if (data["no_incomplete_sessions"]) {
                        msg += " * All sessions complete.\n"
                    }
                    if (data["no_receivers"]) {
                        msg += " * Receiver(s) not available.\n"
                    }
                    if (data["blackedout"]) {
                        msg += " * No observer available.\n"
                    }
                    if (data["prescheduled"]) {
                        msg += " * LST range not available.\n"
                    }
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
