function setToggle(bid) {
    $(bid).click(function() {
        $(bid + "_div").toggle("slow");
        var state = $(bid)[0].innerHTML;
        if (state == "&nbsp;-&nbsp;") {
            $(bid)[0].innerHTML = "&nbsp;+&nbsp;";
        } else {
            $(bid)[0].innerHTML = "&nbsp;-&nbsp;";
        }
    });
}
function initListeners() {
    setToggle("#tp");
    setToggle("#se");
    setToggle("#obs");
    setToggle("#black");
    setToggle("#cal");
}

$(document).ready(function() {
    initListeners();

	$('#calendar').fullCalendar({
        draggable: false,
        events: event_url
	});

});
