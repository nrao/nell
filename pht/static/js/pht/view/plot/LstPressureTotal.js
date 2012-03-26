// map to colors 
var fields = ['Carryover', 
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

Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.LstPressureTotal', {
    extend: 'PHT.view.plot.LstPressurePlot',
    theme: 'LstPressureThemeTotal',
    alias: 'widget.lstpressuretotal',
    /*
    bodyStyle: {
        background: '#fff',
    }, 
    title: 'Lst Pressures',
    width: 300,
    height: 250,
    store: 'LstPressures',
    animate: true,
    shadow: true,
    legend: {
        position: 'right',
    },
    */
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: fields,
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
        yField: fields,
        tips: {
          trackMouse: true,
          width: 300,
          height: 80,
          renderer: function(storeItem, item) {
            // display any non zero values in the tooltip
            // for each column
            var values = [];
            for (f in fields) {
                var field = fields[f];
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

