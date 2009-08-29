function setToggle(bid) {
    $(bid).click(function() {
        $(bid + "_div").toggle("slow");
        var state = $(bid)[0].innerHTML;
        if (state == "-") {
            $(bid)[0].innerHTML = "+";
        } else {
            $(bid)[0].innerHTML = "-";
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
        events: "/project/BB261/blackouts"
	});

});
