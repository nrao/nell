Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressurePoor', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemePoor',
    alias: 'widget.lstpressurepoor',

    initComponent: function() {
        // map to colors 
        this.pressureFields = ['Carryover_Poor', 
                      'Requested_Poor',
                      'Poor_A',
                      'Poor_B',
                      'Poor_C',
        ];
        this.availableField = 'Available_Poor';
        this.callParent();
    },

});

