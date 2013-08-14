Ext.define('PHT.controller.Plots', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'LstPressure',
        'ProposalTimeline',
    ],

    stores: [
        'LstPressures',
        'ProposalTimelines',
        'ProposalCodes',
        'Sessions',
    ],

    views: [
        'plot.Window',
        'plot.LstPressurePlot',
        'plot.LstPressureTotal',
        'plot.LstPressurePoor',
        'plot.LstPressureGood',
        'plot.LstPressureExcellent',
        'plot.LstReportWindow',
        'plot.TimelineWindow',
        'plot.ProposalTimelinePlot',
    ],

    init: function() {
        this.control({
            'plotwindow toolbar button[action=update]': {
                click: this.updatePlot
            },
            'plotwindow toolbar button[action=clear]': {
                click: this.clearFilterCombos
            },           
            'plotwindow toolbar button[action=print]': {
                click: this.printPlot
            },           
            'lstreportwindow button[action=ok]': {
                click: this.lstReport
            },           
            'timelineplotwindow toolbar button[action=update]': {
                click: this.updateTimelinePlot
            },
        }); 

        this.callParent(arguments);
    },

    clearFilterCombos: function(button) {
        var win = button.up('window');
        win.proposalCombo.reset()
        win.sessionCombo.reset()
    },

    lstReport: function(button) {
        var win = button.up('window');
        var form = win.down('form');
        var f = form.getForm();
        // send report request to server
        var values = f.getValues();
        var session = values['session'];
        var debug = values['debug'];
        var carryover = values['carryoverType'];
        var adjust = values['adjustWeatherBins'];
        var sponsors = values['showSponsors'];
        var url = 'reports/lst_pressures?debug=' + debug;
        if ((session != null) && (session != '')) {
            url = url + '&session=' + session
        }
        if ((carryover != null) && (carryover != '')) {
            if (carryover == 'Next Semester Time') {
                var useNextSemester = 'true'
            } else {
                var useNextSemester = 'false'
            }
            url = url + '&carryOverUseNextSemester=' + useNextSemester
        }
        url = url + '&adjustWeatherBins=' + adjust
        url = url + '&showSponsors=' + sponsors
        window.open(url);
        win.hide();
    },

    printPlot: function(button) {
        var win = button.up('window');
        var type = win.plotTypesCombo.value;
        if ((type != null) && (type != '')) {
            var url = 'lst_pressure/print/' + type.toLowerCase();
            // adjust weather bins?
            var adjustWeather = win.down('checkboxfield').value
            console.log('adjust:');
            console.log(adjustWeather);
            if (adjustWeather == true) {
                adjust = 'true'
            } else {
                adjust = 'false'
            }
            url += "?adjustWeatherBins=" + adjust
            // how to handle carryover?
            var carryover = win.carryoverTypesCombo.value 
            if ((carryover != null) & (carryover != "")) {
                if (carryover == 'Next Semester Time') {
                    url += '&carryOverUseNextSemester=true'
                } else {
                    url += '&carryOverUseNextSemester=false'
                }
            }    
                window.open(url);
            }    
    },

    updatePlot: function(button) {
        var win = button.up('window')
        var store = this.getStore('LstPressures');
        // be patient ...
        var storeMask = new Ext.LoadMask(Ext.getBody()
            , {msg:"Loading LST Pressures ...",
               store: store,
              });
        // which sessions are we calculating pressures for?
        var filters = []
        var pcode = win.proposalCombo.value 
        if ((pcode != null) & (pcode != "")) {
            filters.push({property: 'pcode', value: pcode})
        }    
        var sname = win.sessionCombo.value 
        if ((sname != null) & (sname != "")) {
            filters.push({property: 'session', value: sname})
        }    
        // how to handle carryover?
        var carryover = win.carryoverTypesCombo.value 
        if ((carryover != null) & (carryover != "")) {
            filters.push({property: 'carryover', value: carryover})
        }    
        // adjust weather bins?
        
        //var adjustWeather = win.down('checkboxfield').value
        var adjustWeather = win.down('#adjustWeatherBins').value
        filters.push({property: 'adjust', value: adjustWeather})
        // show sponsors?
        //var sponsor = win.down('checkboxfield').value
        var sponsor = win.down('#sponsors').value
        filters.push({property: 'sponsor', value: sponsor})

        if (filters.length == 0) {
            store.load()
        } else {
            store.load({filters: filters})
        }    
    },

    updateTimelinePlot: function(button) {
        var win = button.up('window')
        var store = this.getStore('ProposalTimelines');
        // which sessions are we calculating pressures for?
        var filters = []
        var pcode = win.proposalCombo.value 
        if ((pcode != null) & (pcode != "")) {
            filters.push({property: 'pcode', value: pcode})
        }    
        var sponsor = win.sponsorCombo.value 
        if ((sponsor != null) & (sponsor != "")) {
            filters.push({property: 'sponsor', value: sponsor})
        }    
        if (filters.length == 0) {
            store.load()
        } else {
            store.load({filters: filters})
        }    
    },

});    

