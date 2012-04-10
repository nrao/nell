Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureTotal', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeTotal',
    alias: 'widget.lstpressuretotal',

    initComponent: function() {
        // map to colors 
        this.pressureFields = ['Carryover', 
              'Requested',
              'Poor_A',
              'Poor_B',
              'Poor_C',
              'Good_A',
              'Good_B',
              'Good_C',
              'Excellent_A',
              'Excellent_B',
              'Excellent_C',
        ];        
        this.availableField = 'Available';
        this.callParent();
    },

});

