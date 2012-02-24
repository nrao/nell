Ext.define('PHT.view.overview.Period', {
    extend: 'Ext.draw.Sprite',
    alias: 'widget.overviewperiod',
    constructor: function() {
        this.px2time = Ext.create('PHT.view.overview.PixelsToTime');
        this.day     = 0;
        this.color   = 'red';
        var parentConfig = {
            type: 'rect',
            fill: 'red',
            stroke: 2,
            width: 45,
            height: this.px2time.dayPx,
            opacity: .6,
            x: 100,
            y: this.vertOffset,
            floating: true,
        };

        var me = this;
        this.listeners = {
            click: function() {
                console.log('click');
            },
            mouseover: function() {
                console.log('mouseover');
            },
            mouseout: function() {
                console.log('mouseout');
            },
        };

        this.callParent([parentConfig]);
    },

    setDrawComponent: function(drawComponent){
        this.drawComponent = drawComponent;
        this.drawComponent.items.push(this);
    },

    setData: function(record){
        this.record = record;
    },

    setColor: function(color) {
        this.color = color;
        this.setAttributes({fill: color});
    },

    setDay: function(day) {
        this.day = day;
        this.setAttributes({y: this.px2time.day2px(day)});
    },

    setTime: function(start, duration) {
        var endTime = start + duration;
        if (endTime > 24) {
            duration_prime = endTime - 24;
            duration       = duration - duration_prime;
            this.createSibling(this.day + 1, 0, duration_prime);
        }

        var x     = this.px2time.time2px(start),
            width = this.px2time.duration2px(duration);
        
        this.setAttributes({x : x, width : width});
    },

    createSibling: function(day, start, duration){
        this.sibling = Ext.create('PHT.view.overview.Period');
        this.sibling.setDrawComponent(this.drawComponent);
        this.sibling.setColor(this.color);
        this.sibling.setDay(day);
        this.sibling.setTime(start, duration);
    }

});
