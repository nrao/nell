// map to colors 
var fieldsPoor = ['Carryover_Poor', 
              'Poor_A',
              'Poor_B',
              'Poor_C',
              ];

Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressurePoor', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemePoor',
    alias: 'widget.lstpressurepoor',
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: fieldsPoor,
        grid: true,
        title: 'Pressure (Hrs)',
        minimum: 0,
        //adjustMinimumByMajorUnit: 0
    }, {
        // Using Numeric has some funny consequences.  Since
        // we always know the Ra is between 0 and 23, this is a 
        // sensible axis type to use.
        type: 'Category',
        position: 'bottom',
        grid: true,
        fields: ['LST'],
        title: 'LST',
        label: {
            rotate: {
                degrees: 315
            }
        }
    }],
    series: [{
        type: 'column',
        stacked: true,
        xField: 'LST',
        yField: fieldsPoor,
        tips: {
          trackMouse: true,
          width: 300,
          height: 80,
          renderer: function(storeItem, item) {
            // display any non zero values in the tooltip
            // for each column
            var values = [];
            for (f in fieldsPoor) {
                var field = fieldsPoor[f];
                var value = storeItem.get(field);
                if (value > 0.0) {
                    values.push(' ' + field + ' = ' + value);
                }    
            }
            this.setTitle('LST = ' + storeItem.get('LST') + ': ' + values.join());
          },
        },  
    },{
        type: 'line',
        showMarkers: false,
        xField: 'LST',
        yField: 'Available_Poor',
    }],

});

