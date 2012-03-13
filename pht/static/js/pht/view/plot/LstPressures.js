// We need a color theme where the weather types are very
// different, but one can distinguish the different grades
function getColors(color) {
    var c = new Ext.draw.Color.fromString(color);
    var c1 = c.getLighter(0.15);
    var c2 = c.getLighter(0.30);
    return [c, c1, c2];
}

// The below colors should map to the below fields
var blues = getColors('#0000FF');
var greens = getColors('#00FF00');
var reds = getColors('#FF0000');
var colors = ['orange',
              reds[0].toString(),
              reds[1].toString(), 
              reds[2].toString(), 
              greens[0].toString(),
              greens[1].toString(), 
              greens[2].toString(), 
              blues[0].toString(),
              blues[1].toString(), 
              blues[2].toString(), 
             ];

// map to colors above
var fields = ['carryover', 
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

// We use this theme in our chart 
Ext.define('Ext.chart.theme.LstPressureTheme', {
    extend: 'Ext.chart.theme.Base',
 
    constructor: function(config) {
        this.callParent([Ext.apply({
            colors: colors
        }, config)]);
    }
});

Ext.define('PHT.view.plot.LstPressures', {
    extend: 'Ext.chart.Chart',
    theme: 'LstPressureTheme',
    alias: 'widget.lstpressureplot',
    bodyStyle: {
        background: '#fff',
    }, 
    title: 'Lst Pressures',
    width: 600,
    height: 500,
    store: 'LstPressures',
    animate: true,
    shadow: true,
    legend: {
        position: 'right',
    },    
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: fields,
        grid: true,
        title: 'Pressure (Hrs)',
        minimum: 0,
        //adjustMinimumByMajorUnit: 0
    }, {
        type: 'Numeric',
        position: 'bottom',
        grid: true,
        fields: ['ra'],
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
        xField: 'ra',
        yField: fields,
        tips: {
          trackMouse: true,
          width: 300,
          height: 80,
          renderer: function(storeItem, item) {
            var values = [];
            for (f in fields) {
                var field = fields[f];
                var value = storeItem.get(field);
                console.log(field);
                console.log(value);
                if (value > 0.0) {
                    values.push(' ' + field + ' = ' + value);
                }    
            }
             
            this.setTitle('LST = ' + storeItem.get('ra') + ': ' + values.join());
          },
        },  
    },{
        type: 'line',
        showMarkers: false,
        xField: 'ra',
        yField: 'available',
    }],

});

