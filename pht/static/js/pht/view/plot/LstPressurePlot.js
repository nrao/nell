Ext.define('PHT.view.plot.LstPressurePlot', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.lstpressureplot',
    bodyStyle: {
        background: '#fff',
    }, 
    store: 'LstPressures',
    animate: true,
    shadow: true,
    legend: {
        position: 'right',
        labelFont: '6px Helvetica, sans-serif',
    },  

    initComponent: function() {
        var me = this;
        this.axes = [{
            // X-Axis:
            // Using Numeric has some funny consequences.  Since
            // we always know the Ra is between 0 and 23, this is a 
            // sensible axis type to use.
            type: 'Category',
            position: 'bottom',
            grid: true,
            fields: ['LST'],
            title: 'LST',
            label: {
                font: '7px Helvetica, sans-serif',
                rotate: {
                    degrees: 315
                }
            }
          },{
            // Y-Axis:
            type: 'Numeric',
            position: 'left',
            fields: this.pressureFields.concat([this.availableField]),
            grid: true,
            title: 'Pressure (Hrs)',
            label: {
                font: '7px Helvetica, sans-serif',
            }
        }];
        this.series = [{
            // Pressure data
            type: 'column',
            stacked: true,
            xField: 'LST',
            yField: this.pressureFields,
            tips: {
              trackMouse: true,
              width: 300,
              height: 80,
              scope: this,
              renderer: function(storeItem, item) {
                // display any non zero values in the tooltip
                // for each column
                var values = [];
                for (f in me.pressureFields) {
                    var field = me.pressureFields[f];
                    var value = storeItem.get(field);
                    if (value > 0.0) {
                        values.push(' ' + field + ' = ' + value.toFixed(3));
                    }    
                }
                this.setTitle('LST = ' + storeItem.get('LST') + ': ' + values.join());
              },
            },
        },{
            // Availability data
            type: 'line',
            showMarkers: false,
            xField: 'LST',
            yField: [this.availableField],
            style: {
                fill: '#000000',
                stroke: '#000000',
                'stroke-width': 2
            },
        }];
        this.callParent();
    },
});

