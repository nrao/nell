Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureGood', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeGood',
    alias: 'widget.lstpressuregood',
    initComponent: function() {
        this.pressureFields = ['Carryover_Good', 
                      'Good_A',
                      'Good_B',
                      'Good_C',
                      'Requested_Good',
                      'WVU_Good',
        ];

        // map to colors 
        this.availableField = 'Available_Good';

        this.callParent();
    },

});

