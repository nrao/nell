Ext.define('PHT.view.plot.LstPressures', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.lstpressureplot',
    bodyStyle: {
        background: '#fff',
    }, 
    title: 'Lst Pressures',
    width: 400,
    height: 300,
    store: 'LstPressures',
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: ['pressure'],
        title: 'Pressure (Hrs)',
        minimum: 0,
        //adjustMinimumByMajorUnit: 0
    }, {
        type: 'Numeric',
        position: 'bottom',
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
        xField: 'ra',
        yField: ['pressure'], 
    }],

});

