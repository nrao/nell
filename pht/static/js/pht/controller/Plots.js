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
        this.callParent(arguments);

    },
});    

