Ext.define('PHT.view.overview.Period', {
    extend: 'Ext.draw.Sprite',
    alias: 'widget.overviewperiod',
    constructor: function() {
        this.px2time = Ext.create('PHT.view.overview.PixelsToTime');
        this.day     = 0;
        this.color   = 'red';
        this.periodType = '';
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
                var view   = Ext.widget('periodedit');
                view.down('form').loadRecord(this.record);        
            },
            mouseover: function(me, e) {
                me.tooltip.showAt(e.getXY());
            },
            mouseout: function() {
                me.tooltip.hide();
            },
        };

        this.callParent([parentConfig]);
    },

    setDrawComponent: function(drawComponent){
        this.drawComponent = drawComponent;
        this.drawComponent.items.push(this);
    },

    setPeriodType: function(type) {
        this.periodType = type;
    },

    setData: function(record, type, receivers){
        this.record = record;
        if (this.sibling) {
            this.sibling.setData(record);
        }

        if (this.record.get('session').type == 'elective'){
            this.setColor('purple');
        } else if (this.record.get('session').type == 'fixed'){
            this.setColor('red');
        } else if (this.record.get('session').type == 'windowed'){
            if (this.record.get('session').guaranteed) {
                this.setColor('green');
            } else {
                this.setColor('yellow');
            }
        } else if (this.record.get('session').type == 'open'){
            this.setColor('blue');
        }
        if (this.record.get('session').science == 'maintenance'){
            this.setColor('orange');
        }

        var id = type + '_' + record.get('id');

        this.setAttributes({id : id })
        this.tooltip = Ext.create('Ext.tip.ToolTip', {
            target: id,
            title: record.get('handle'),
            html: 'Start Date: ' + record.get('date') + ' at ' + record.get('time') + '<br/>' +
                  'Duration: ' + record.get('duration') + '<br/>' +
                  'Receiver(s): ' + receivers, 
            width: 250,
            dismissDelay: 0,
        });

    },

    setColor: function(color) {
        this.color = color;
        this.setAttributes({fill: color});
    },

    setDay: function(day) {
        this.day = day;
        this.y   = this.px2time.day2px(day);
        this.setAttributes({y: this.y});
    },

    setTime: function(start, duration) {
        var endTime = start + duration;
        if (endTime > 24) {
            duration_prime = endTime - 24;
            duration       = duration - duration_prime;
            this.createSibling(this.day + 1, 0, duration_prime);
        }

        this.x     = this.px2time.time2px(start),
        this.width = this.px2time.duration2px(duration);
        
        this.setAttributes({x : this.x, width : this.width});
    },

    createSibling: function(day, start, duration){
        this.sibling = Ext.create('PHT.view.overview.Period');
        this.sibling.setDrawComponent(this.drawComponent);
        this.sibling.setDay(day);
        this.sibling.setTime(start, duration);
    }

});
