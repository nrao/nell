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
        }); 

        this.callParent(arguments);
    },

    clearFilterCombos: function(button) {
        var win = button.up('window');
        win.proposalCombo.reset()
        win.sessionCombo.reset()
    },

    updatePlot: function(button) {
        var win = button.up('window')
        var store = this.getStore('LstPressures');
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

