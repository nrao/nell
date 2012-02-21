Ext.define('PHT.view.overview.Period', {
    extend: 'Ext.draw.Sprite',
    alias: 'widget.overviewperiod',
    constructor: function() {
        var parentConfig = {
            type: 'rect',
            fill: 'red',
            width: 50,
            height: 25,
            x: 100,
            y: 10,
            floating: true,
        };
        this.callParent([parentConfig]);
    },
    listeners: {
        click: function() {
            console.log('click');
        },
        mouseover: function() {
            console.log('mouseover');
        },
        mouseout: function() {
            console.log('mouseout');
        },
    },
});
