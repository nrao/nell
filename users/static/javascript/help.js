function showHelp() {
    window.open('http://libraryh3lp.com/chat/nrao-dss@chat.libraryh3lp.com', 'chat', 'width=400,height=320');
}

function initHelp() {
    var i = 0;
    for (var i = 0; i < jabber_resources.length; ++i) {
        var resource = jabber_resources[i];
        if (resource.show == 'available') {
            $('#help').show();
            return;
        }
    }
}

function showOfflineHelp() {
    parent.location='mailto:helpdesk-dss@gb.nrao.edu'
}

function initOfflineHelp() {
    var i = 0;
    for (var i = 0; i < jabber_resources.length; ++i) {
        var resource = jabber_resources[i];
        if (resource.show != 'available') {
            $('#offlinehelp').show();
            return;
        }
    }
}

$(document).ready(function() {
    initOfflineHelp();
    initHelp();
});
