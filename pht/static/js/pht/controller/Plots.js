Ext.define('PHT.controller.Plots', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'LstPressure',
    ],

    stores: [
        'LstPressures',
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
                click: this.drawPlot
            },
            
        }); 

        this.callParent(arguments);
    },

    drawPlot: function() {
        var store = this.getStore('LstPressures');
        store.load();
    },

});    

