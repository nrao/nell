Ext.define('PHT.view.overview.Calendar', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.overviewcalendar',
    bodyStyle: {
        background: '#fff',
    }, 

    initComponent: function() {
        var me      = this;
        var days = Ext.create('Ext.data.Store', {
            fields: ['day'],
            data:[
                {'day' : 7},
                {'day' : 14},
                {'day' : 30},
                {'day' : 45},
                {'day' : 60},
                {'day' : 90},
                ]
        });
        this.numDaysCombo  = Ext.create('Ext.form.field.ComboBox', {
                    fieldLabel: 'Days',
                    store: days,
                    queryMode: 'local',
                    displayField: 'day',
                    valueField: 'day',
                    value: '30',
                    labelAlign: 'right',
                    labelWidth: 30,
        });
        this.startDateField = Ext.create('Ext.form.field.Date', {
            name: 'startDate',
            value: new Date(),
            fieldLabel: 'Start Date',
            labelAlign: 'right',
            labelWidth: 60,
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.startDateField,
                this.numDaysCombo,
                {
                    text: 'Update',
                    action: 'update',
                },
            ]
        }];
        this.callParent(arguments);
    },

    genDrawComponent: function(numDays){
        var me      = this;
        this.periods = [];
        this.px2time = Ext.create('PHT.view.overview.PixelsToTime');
        this.hourPx = this.px2time.hourPx; // # of pixels for an hour
        this.dayPx  = this.px2time.dayPx; // # of pixels for a day
        this.width  = 25 * this.hourPx + 100 - this.hourPx;
        this.height = (numDays + 1) * this.dayPx - this.dayPx;

        var drawComponent = Ext.create('Ext.draw.Component', {
            height: '100%',
            width: '100%',
            autoScroll: true,
            items: [
                {
                    type: 'path',
                    stroke: 'lightgray',
                    path: me.generateQuarterLines(numDays),
                },
                {
                    type: 'path',
                    stroke: '#000',
                    path: me.generateGridPath(numDays),
                },
                {
                    type: 'text',
                    text: 'Rcvrs',
                    x: this.width + 15,
                    y: 0
                },
            ]
        });
        this.labelHours(drawComponent);
        this.labelDays(drawComponent, numDays);
        return drawComponent;
    },

    addRcvrList: function(drawComponent, day, rcvrStr) {
        drawComponent.items.push({
            type: 'text',
            text: rcvrStr,
            x: this.width + 15,
            y: this.px2time.day2px(parseInt(day)) + 10
        });
    },

    labelDays: function(drawComponent, numDays) {
        //  Need to copy the date object from the picker 
        //  because we'll modify it below.
        var calDate = new Date(this.startDateField.getValue().toUTCString());
        var start   = 20;
        var text    = '';
        var day     = 0;
        var rowLabel;
        var month = new Array( "Jan", "Feb", "Mar", "Apr", "May",
            "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");

        for (i = 0; i < numDays; i++){
            day = calDate.getUTCDate();
            if (day == 1 | i == 0) {
                text = month[calDate.getUTCMonth()] + " " + day;

            } else {
                text = day;
            }

            rowLabel = Ext.create('Ext.draw.Sprite', {
                type: 'text',
                'text-anchor': 'end',
                text: text,
                x: 90,
                y: start
            });
            drawComponent.items.push(rowLabel);
            start += this.dayPx;
            calDate.setDate(day + 1);
        }
    },

    labelHours: function(drawComponent) {
        var start = 100;
        for (i = 0; i < 24; i++){
            drawComponent.items.push({
                type: 'text',
                text: i,
                x: start,
                y: 0
            });
            if (i == 9) {
                start -= 5;
            }
            start += this.hourPx;
        }
    },

    generateGridPath: function(numDays) {
        var numCols = 25; // number of hours + 1
        var start   = 100;
        var width   = numCols * this.hourPx + start - this.hourPx;
        var numRows = numDays + 1;
        var height  = numRows * this.dayPx + 10 - this.dayPx;
        var path    = [];
        for (c = 0; c < numCols; c++) {
            path.push('M' + start + ' 10');
            path.push('L' + start + ' ' + height);
            start += this.hourPx;
        }
        start = 10;
        for (r = 0; r < numRows; r++) {
            path.push('M100 ' + start);
            path.push('L' + width + ' ' + start);
            start += this.dayPx;
        }
        return path;
    },

    generateQuarterLines: function(numDays) {
        var numCols = 24;
        var start   = 100;
        var width   = numCols * this.hourPx + start - this.hourPx;
        var numRows = numDays + 1;
        var height  = numRows * this.dayPx + 10 - this.dayPx;
        var path   = [];
        for (c = 0; c < numCols; c++) {
            path.push('M' + (start + (this.hourPx / 4.0)) + ' 10');
            path.push('L' + (start + (this.hourPx / 4.0)) + ' ' + height);
            path.push('M' + (start + (this.hourPx / 2.0)) + ' 10');
            path.push('L' + (start + (this.hourPx / 2.0)) + ' ' + height);
            path.push('M' + (start + (this.hourPx * 3 / 4.0)) + ' 10');
            path.push('L' + (start + (this.hourPx * 3 / 4.0)) + ' ' + height);
            start += this.hourPx;
        }
        return path;
    },

    highlight: function(periods){
        for (i in this.periods){
            if(this.periods[i].record.get('id') == periods[0].get('id')){
                this.periods[i].selected();
            } else {
                this.periods[i].unselected();
            }
        }
    },

    addPeriod: function(period){
        this.periods.push(period);
    },

    close: function() {
        this.hide();
    }
});
