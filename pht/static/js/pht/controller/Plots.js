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
        }); 

        this.callParent(arguments);
    },

    clearFilterCombos: function(button) {
        var win = button.up('window');
        win.proposalCombo.reset()
        win.sessionCombo.reset()
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

