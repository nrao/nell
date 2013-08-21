Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureTotal', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeTotal',
    alias: 'widget.lstpressuretotal',

    initComponent: function() {

/*
        Karen wants the data to appear in the following order, from bottom to top:
        * carryover
        * new astronomy:
          * Grade A:
            * Excellent
            * Good
            * Poor
          * Grade B:
            * same weather order
          * Grade C:
            * same weather order
        * requested    
*/

        // map to colors 
        this.pressureFields = ['Carryover', 
              'Excellent_A',
              'Good_A',
              'Poor_A',
              'Excellent_B',
              'Good_B',
              'Poor_B',
              'Excellent_C',
              'Good_C',
              'Poor_C',
              'WVU',
              'Requested',
        ];        
        this.availableField = 'Available';
        this.callParent();
    },

});

