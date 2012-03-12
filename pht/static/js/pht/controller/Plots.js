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
        'plot.LstPressures',
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

