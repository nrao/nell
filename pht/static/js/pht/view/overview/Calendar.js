Ext.define('PHT.view.overview.Calendar', {
    extend: 'Ext.window.Window',
    autoScroll: true,
    width: '90%',
    height: '90%',
    layout: 'fit',
    constrainHeader: true,
    title: 'Overview Calendar',
    maximizable: true,
    bodyStyle: {
        background: '#fff',
    }, 

    initComponent: function() {
        var me      = this;
        this.startDateMenu = Ext.create('Ext.menu.DatePicker', { });
        this.items  = [this.genDrawComponent(45)];
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
                    value: '45',
                    labelAlign: 'right',
                    labelWidth: 30,
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                {
                    text: 'Start Date',
                    menu: this.startDateMenu 
                },
                this.numDaysCombo,
                {
                    text: 'Update',
                    action: 'update',
                    listeners: {
                        click: function(button){
                            me.removeAll(true);
                            me.add(me.genDrawComponent(me.numDaysCombo.getValue()));
                            me.doLayout();
                        }
                    },
                },
            ]
        }];
        this.callParent(arguments);
    },

    genDrawComponent: function(numDays){
        var me      = this;
        this.px2time = Ext.create('PHT.view.overview.PixelsToTime');
        this.hourPx = this.px2time.hourPx; // # of pixels for an hour
        this.dayPx  = this.px2time.dayPx; // # of pixels for a day
        this.width  = 25 * this.hourPx + 100 - this.hourPx;
        this.height = (numDays + 1) * this.dayPx - this.dayPx;

        var drawComponent = Ext.create('Ext.draw.Component', {
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
                    type: 'rect',
                    stroke: '#000',
                    height: this.height,
                    width: 60,
                    x: this.width + 10,
                    y: 10
                },
                {
                    type: 'text',
                    text: 'Rcvrs',
                    x: this.width + 15,
                    y: 0
                }
            ]
        });
        this.labelHours(drawComponent);
        this.labelDays(drawComponent, numDays);
        this.insertPeriods(drawComponent);
        return drawComponent;
    },

    insertPeriods: function(drawComponent) {
        // Some test periods for now.
        var period  = Ext.create('PHT.view.overview.Period');
        period.setDrawComponent(drawComponent);
        period.setColor('blue');
        period.setDay(4);
        period.setTime(1.75, 4.5);
        drawComponent.items.push(period);

        period  = Ext.create('PHT.view.overview.Period');
        period.setDrawComponent(drawComponent);
        period.setColor('red');
        period.setDay(8);
        period.setTime(10.5, 8.5);
        drawComponent.items.push(period);

        period  = Ext.create('PHT.view.overview.Period');
        period.setDrawComponent(drawComponent);
        period.setColor('purple');
        period.setDay(8);
        period.setTime(5.0, 6);
        drawComponent.items.push(period);

        period  = Ext.create('PHT.view.overview.Period');
        period.setDrawComponent(drawComponent);
        period.setColor('green');
        period.setDay(5);
        period.setTime(20.0, 8.0);
        drawComponent.items.push(period);
    },

    labelDays: function(drawComponent, numDays) {
        var calDate = new Date(this.startDateMenu.picker.getValue().toUTCString());
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
        var start = 125;
        for (i = 0; i < 24; i++){
            drawComponent.items.push({
                type: 'text',
                text: i,
                x: start,
                y: 0
            });
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

    close: function() {
        this.hide();
    }
});
