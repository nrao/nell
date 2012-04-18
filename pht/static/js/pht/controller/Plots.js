Ext.define('PHT.controller.Plots', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'LstPressure',
    ],

    stores: [
        'LstPressures',
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
        var url = 'reports/lst_pressures?debug=' + debug;
        if ((session != null) && (session != '')) {
            url = url + '&session=' + session
        }
        window.open(url);
        win.hide();
    },

    printPlot: function(button) {
        var win = button.up('window');
        var type = win.plotTypesCombo.value;
        if ((type != null) && (type != '')) {
            var url = 'lst_pressure/print/' + type.toLowerCase();
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
        if (filters.length == 0) {
            store.load()
        } else {
            store.load({filters: filters})
        }    
    },

});    

