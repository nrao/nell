Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureExcellent', {

    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeEx',
    alias: 'widget.lstpressureexcellent',

    initComponent: function() {
        // map to colors 
        this.pressureFields = ['Carryover_Excellent', 
                      'Requested_Excellent',
                      'Excellent_A',
                      'Excellent_B',
                      'Excellent_C',
        ];
        this.availableField = 'Available_Excellent';
        this.callParent();
    },

});

