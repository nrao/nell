Ext.require('PHT.view.plot.PlotTheme');

Ext.define('PHT.view.plot.ProposalTimelinePlot', {
    extend: 'Ext.chart.Chart',
    //theme: 'LstPressureThemeTotal',
    alias: 'widget.timelineplot',
    store: 'ProposalTimelines',

    initComponent: function() {
        var me = this;
        this.axes = [{
            // X-Axis:
            // Can't get Time to work properly
            //type: 'Time',
            type: 'Category',
            position: 'bottom',
            //grid: true,
            fields: ['date'],
            title: 'Date',
            /*
            dateFormat: 'd/m/Y',
            fromDate: Date(2013, 1, 1),
            toDate: Date(2013, 9, 1),
            */
            label: {
                font: '9px Helvetica, sans-serif',
                rotate: {
                    degrees: 315
                }
            }
          },{
            // Y-Axis:
            type: 'Numeric',
            position: 'left',
            fields: ['hrs', 'allocated'], 
            grid: true,
            title: 'Time Billed (Hrs)',
            label: {
                font: '7px Helvetica, sans-serif',
            }
        }];

       this.series = [{
            type: 'line',
            showMarkers: false,
            xField: 'date',
            yField: 'hrs', 
        },
        {
            type: 'line',
            showMarkers: false,
            xField: 'date',
            yField: 'allocated', 
        },
        ];

        this.callParent();
    },

});

