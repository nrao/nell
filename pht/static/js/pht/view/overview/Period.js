Ext.define('PHT.view.overview.Period', {
    extend: 'Ext.draw.Sprite',
    alias: 'widget.overviewperiod',
    constructor: function() {
        this.px2time = Ext.create('PHT.view.overview.PixelsToTime');
        this.day     = 0;
        this.color   = 'red';
        this.periodType = '';
        // map color names to hex values
        this.colors = { red:  '#FF0000',
                        green: '#00FF00',
                        blue: '#0000FF',
                        purple: '#800080',
                        yellow: '#FFFF00',
                        orange: '#FFA500',
                      };
        // map a type of box on the calendar to a color           
        this.session2color = { open: 'blue',
                             fixed: 'red',
                             defaultWindowed: 'yellow',
                             chosenWindowed: 'green',
                             elective: 'purple',
                             maintenance: 'orange',
                             };

        var parentConfig = {
            type: 'rect',
            fill: 'red',
            stroke: 2,
            width: 45,
            height: this.px2time.dayPx,
            opacity: 0.3,
            x: 100,
            y: this.vertOffset,
            floating: true,
        };

        var me = this;
        this.listeners = {
            click: function() {
                if (me.periodType != 'dss'){
                    var view   = Ext.widget('periodedit');
                    view.down('form').loadRecord(this.record);
                }
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

    setPeriodType: function(pType) {
        this.periodType = pType;
    },

    setData: function(record, pType, receivers){
        this.record = record;
        if (this.sibling) {
            this.sibling.setData(record, pType, receivers);
        }

        var description = 'Start Date: ' + record.get('date') + ' at ' + record.get('time') +
                          '<br/>Duration: ' + record.get('duration') + 'hrs' +
                          '<br/>Receiver(s): ' + receivers; 

        // figure out how to display these periods - remember 
        // that DSS and PHT periods are a little different
        var sessionType;
        var observingType;
        var boxType;
        this.setPeriodType(pType);
        if (pType == 'dss') {
            sessionType =  this.record.get('session').type.toLowerCase()
            observingType = this.record.get('session').science.toLowerCase()
        } else {
            sessionType =  this.record.get('session_json').type.toLowerCase()
            observingType = this.record.get('session_json').observing_type.toLowerCase()
            // there are 3 different types of PHT open sessions
            if (sessionType.search("open") != -1) {
                sessionType = "open";
            }
        }
        
        // each 'box' on the calendar is a period, and we are mapping
        // many different period attributes to one attribute of this
        // box: the color.
        if (observingType == 'maintenance') {
            boxType = 'maintenance'
        } else if (sessionType == 'windowed') {
            description += '<br/>Window Start: ' + record.get("wstart") +
                           '<br/>Window End: ' + record.get("wend");
            if (this.record.get('wdefault')) {
                boxType = 'defaultWindowed'
            } else {
                boxType = 'chosenWindowed'
            }
        } else {
            boxType = sessionType
        }

        this.setColor(this.session2color[boxType], pType)

        var id = pType + '_' + record.get('id');

        this.setAttributes({id : id })
        this.tooltip = Ext.create('Ext.tip.ToolTip', {
            target: id,
            title: record.get('handle'),
            html: description,
            width: 250,
            dismissDelay: 0,
        });

    },

    setColor: function(colorName, pType) {
        var color = this.colors[colorName]
        var c = new Ext.draw.Color.fromString(color);
        // distinguish the PHT from DSS periods 
        if (pType == 'pht') {
            // factor defaults to .2; .5 makes blue white!
            c = c.getLighter()
        }
        this.color = c.toString(); //color;
        this.setAttributes({fill: c.toString()}); //color});
    },

    selected: function() {
        this.setAttributes({opacity: 1}, true);
    },

    unselected: function() {
        this.setAttributes({opacity: .3}, true);
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
