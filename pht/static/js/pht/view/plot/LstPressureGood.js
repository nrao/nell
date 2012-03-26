// map to colors 
var fieldsGood = ['Carryover_Good', 
              'Good_A',
              'Good_B',
              'Good_C',
              ];
Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureGood', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeGood',
    alias: 'widget.lstpressuregood',
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: fieldsGood,
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
        yField: fieldsGood,
        tips: {
          trackMouse: true,
          width: 300,
          height: 80,
          renderer: function(storeItem, item) {
            // display any non zero values in the tooltip
            // for each column
            var values = [];
            for (f in fieldsGood) {
                var field = fieldsGood[f];
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
        yField: 'Available',
    }],

});

